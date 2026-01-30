# ============================================================================
# FILE: core/models/analysis_result.py
# Immutable Analysis Result - Single Source of Truth
# ============================================================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


@dataclass(frozen=True)
class AnalysisMetadata:
    """
    Metadata about the analysis execution
    
    frozen=True makes this immutable
    """
    analysis_id: str
    timestamp: str
    duration_seconds: float
    pipeline_version: str
    ee_available: bool
    osm_quality: str  # 'real_osm', 'enhanced', 'mock', 'unknown'
    ml_enabled: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'analysis_id': self.analysis_id,
            'timestamp': self.timestamp,
            'duration_seconds': self.duration_seconds,
            'pipeline_version': self.pipeline_version,
            'ee_available': self.ee_available,
            'osm_quality': self.osm_quality,
            'ml_enabled': self.ml_enabled
        }


@dataclass(frozen=True)
class AnalysisResult:
    """
    Complete, immutable analysis result
    
    PHILOSOPHY:
    - Created once by AnalysisPipeline
    - Never modified after creation
    - Contains ALL analysis outputs
    - UI reads this, never computes
    
    frozen=True ensures immutability at Python level
    """
    
    # Metadata
    metadata: AnalysisMetadata
    
    # Input boundary
    boundary: Dict
    
    # Extracted features
    features: Dict
    
    # Risk assessment (from RiskEngine)
    risk_assessment: Any  # ComprehensiveRiskResult
    
    # Suitability scores (from AHP)
    suitability: Dict
    
    # Recommendations (from UsageRecommender)
    recommendations: List[Dict]
    
    # Summary metrics
    overall_score: float
    confidence_level: float
    
    # Computed properties (cached)
    _key_insights: Optional[Dict] = field(default=None, compare=False, repr=False)
    _summary_text: Optional[str] = field(default=None, compare=False, repr=False)
    
    def __post_init__(self):
        """Validate result after creation"""
        # Basic validation
        if not 0 <= self.overall_score <= 10:
            raise ValueError(f"Invalid overall_score: {self.overall_score}")
        
        if not 0 <= self.confidence_level <= 1:
            raise ValueError(f"Invalid confidence_level: {self.confidence_level}")
    
    # ========== PROPERTIES (read-only access to nested data) ==========
    
    @property
    def analysis_id(self) -> str:
        """Get analysis ID"""
        return self.metadata.analysis_id
    
    @property
    def timestamp(self) -> str:
        """Get analysis timestamp"""
        return self.metadata.timestamp
    
    @property
    def area_hectares(self) -> float:
        """Get area in hectares"""
        return self.boundary.get('area_hectares', 0)
    
    @property
    def area_acres(self) -> float:
        """Get area in acres"""
        return self.boundary.get('area_acres', 0)
    
    @property
    def centroid(self) -> List[float]:
        """Get boundary centroid [lon, lat]"""
        return self.boundary.get('centroid', [0, 0])
    
    @property
    def terrain(self) -> Dict:
        """Get terrain features"""
        return self.features.get('terrain', {})
    
    @property
    def environmental(self) -> Dict:
        """Get environmental features"""
        return self.features.get('environmental', {})
    
    @property
    def infrastructure(self) -> Dict:
        """Get infrastructure features"""
        return self.features.get('infrastructure', {})
    
    @property
    def overall_risk_level(self) -> str:
        """Get overall risk level name"""
        return self.risk_assessment.overall_level.name.lower().replace('_', ' ')
    
    @property
    def risk_summary(self) -> List[str]:
        """Get risk summary lines"""
        return self.risk_assessment.summary
    
    @property
    def top_recommendation(self) -> Optional[Dict]:
        """Get top recommendation"""
        return self.recommendations[0] if self.recommendations else None
    
    @property
    def high_risk_count(self) -> int:
        """Get count of high-severity risks"""
        return self.risk_assessment.high_risk_count
    
    @property
    def data_sources(self) -> Dict:
        """Get data quality information"""
        return {
            'terrain': self.terrain.get('data_quality', 'unknown'),
            'environmental': self.environmental.get('data_quality', 'unknown'),
            'infrastructure': self.infrastructure.get('data_quality', 'unknown'),
            'earth_engine': self.metadata.ee_available,
            'osm': self.metadata.osm_quality,
            'ml': self.metadata.ml_enabled
        }
    
    # ========== COMPUTED INSIGHTS (cached) ==========
    
    @property
    def key_insights(self) -> Dict:
        """
        Get computed key insights
        
        Computed once and cached (using __dict__ hack for frozen dataclass)
        """
        if self._key_insights is None:
            # Compute insights
            insights = self._compute_insights()
            # Cache it (this works even with frozen=True)
            object.__setattr__(self, '_key_insights', insights)
        
        return self._key_insights
    
    def _compute_insights(self) -> Dict:
        """Compute key insights from analysis"""
        
        insights = {
            'strengths': [],
            'concerns': [],
            'opportunities': [],
            'location_summary': '',
            'accessibility_summary': '',
            'development_potential': ''
        }
        
        # Strengths
        if self.terrain.get('slope_avg', 999) < 5:
            insights['strengths'].append(
                f"Gentle terrain: {self.terrain.get('slope_avg', 0):.1f}° slope ideal for construction"
            )
        
        road_dist = self.infrastructure.get('nearest_road_distance', 999999)
        if road_dist < 500:
            insights['strengths'].append(
                f"Excellent access: {road_dist:.0f}m to nearest road"
            )
        
        if self.high_risk_count == 0:
            insights['strengths'].append("No high-severity environmental risks identified")
        
        # Concerns
        if self.high_risk_count > 0:
            insights['concerns'].append(
                f"⚠️ {self.high_risk_count} high-severity risk(s) require mitigation"
            )
        
        if road_dist > 2000:
            insights['concerns'].append(
                f"Limited road access: {road_dist/1000:.1f}km from nearest road"
            )
        
        # Opportunities
        if self.overall_score > 8:
            insights['opportunities'].append(
                "Exceptional suitability - strong development potential"
            )
        
        dev_pressure = self.infrastructure.get('development_pressure', 'low')
        if dev_pressure == 'high':
            insights['opportunities'].append(
                "High development pressure indicates strong market demand"
            )
        
        # Summaries
        city = self.infrastructure.get('city_name', 'Unknown')
        urban_level = self.infrastructure.get('urbanization_level', 'unknown')
        insights['location_summary'] = f"{city}, {urban_level} area"
        
        access_score = self.infrastructure.get('accessibility_score', 0)
        insights['accessibility_summary'] = (
            f"Accessibility score: {access_score:.1f}/10"
        )
        
        if self.overall_score > 8:
            potential = "Exceptional development potential"
        elif self.overall_score > 6:
            potential = "Strong development potential with manageable constraints"
        elif self.overall_score > 4:
            potential = "Moderate potential - careful planning required"
        else:
            potential = "Limited potential - significant constraints present"
        
        insights['development_potential'] = potential
        
        return insights
    
    @property
    def summary_text(self) -> str:
        """
        Get human-readable summary text
        
        Computed once and cached
        """
        if self._summary_text is None:
            summary = self._generate_summary_text()
            object.__setattr__(self, '_summary_text', summary)
        
        return self._summary_text
    
    def _generate_summary_text(self) -> str:
        """Generate summary text"""
        
        lines = [
            f"LAND ANALYSIS SUMMARY",
            f"=" * 50,
            f"",
            f"Analysis ID: {self.analysis_id}",
            f"Date: {self.timestamp}",
            f"",
            f"LOCATION",
            f"  Area: {self.area_hectares:.2f} hectares ({self.area_acres:.2f} acres)",
            f"  Coordinates: {self.centroid[1]:.4f}°N, {self.centroid[0]:.4f}°E",
            f"  {self.key_insights['location_summary']}",
            f"",
            f"OVERALL ASSESSMENT",
            f"  Suitability Score: {self.overall_score:.1f}/10",
            f"  Confidence: {self.confidence_level * 100:.0f}%",
            f"  Overall Risk: {self.overall_risk_level.title()}",
            f"  {self.key_insights['development_potential']}",
            f"",
        ]
        
        # Top recommendation
        if self.top_recommendation:
            rec = self.top_recommendation
            lines.extend([
                f"TOP RECOMMENDATION",
                f"  {rec['usage_type']}: {rec['suitability_score']:.1f}/10",
                f""
            ])
        
        # Risk summary
        if self.risk_summary:
            lines.append("RISK SUMMARY")
            for line in self.risk_summary[:3]:  # Top 3
                lines.append(f"  {line}")
            lines.append("")
        
        # Data quality
        lines.extend([
            f"DATA QUALITY",
            f"  Terrain: {self.data_sources['terrain']}",
            f"  Infrastructure: {self.data_sources['infrastructure']}",
            f"  Earth Engine: {'Available' if self.data_sources['earth_engine'] else 'Not Available'}",
        ])
        
        return "\n".join(lines)
    
    # ========== SERIALIZATION ==========
    
    def to_dict(self, include_full_features: bool = True) -> Dict:
        """
        Convert to dictionary (for storage/API)
        
        Args:
            include_full_features: If False, excludes large feature dicts
        """
        result = {
            'metadata': self.metadata.to_dict(),
            'boundary': {
                'area_hectares': self.area_hectares,
                'area_acres': self.area_acres,
                'centroid': self.centroid,
                'perimeter_m': self.boundary.get('perimeter_m', 0)
            },
            'overall_score': self.overall_score,
            'confidence_level': self.confidence_level,
            'risk': {
                'overall_level': self.overall_risk_level,
                'average_severity': self.risk_assessment.average_severity,
                'high_risk_count': self.high_risk_count,
                'summary': self.risk_summary
            },
            'recommendations': self.recommendations[:5],  # Top 5
            'key_insights': self.key_insights,
            'data_sources': self.data_sources
        }
        
        if include_full_features:
            result['features'] = self.features
            result['suitability'] = self.suitability
        
        return result
    
    def to_json(self, include_full_features: bool = False, indent: int = 2) -> str:
        """Convert to JSON string"""
        data = self.to_dict(include_full_features=include_full_features)
        return json.dumps(data, indent=indent, default=str)
    
    def to_legacy_format(self) -> Dict:
        """
        Convert to legacy format for backward compatibility
        
        This allows gradual migration of UI code
        """
        return {
            'analysis_id': self.analysis_id,
            'timestamp': self.timestamp,
            'boundary': self.boundary,
            'features': self.features,
            'overall_score': self.overall_score,
            'confidence_level': self.confidence_level,
            'risk_assessment': {
                'level': self.overall_risk_level,
                'risk_count': self.high_risk_count,
                'comprehensive_data': self._risk_to_legacy_format()
            },
            'recommendations': self.recommendations,
            'key_insights': self.key_insights,
            'data_sources': self.data_sources,
            'final_scores': {
                'overall_score': self.overall_score,
                'ahp_score': self.suitability.get('overall_score', 0),
                'confidence': self.confidence_level
            }
        }
    
    def _risk_to_legacy_format(self) -> Dict:
        """Convert risk result to legacy comprehensive_risks format"""
        
        def risk_to_dict(risk_assessment):
            return {
                'level': risk_assessment.level.name.lower(),
                'severity': risk_assessment.severity,
                'score': risk_assessment.score,
                'primary_factors': risk_assessment.primary_factors,
                'description': risk_assessment.description,
                'impact': risk_assessment.impact
            }
        
        return {
            'flood': risk_to_dict(self.risk_assessment.flood),
            'landslide': risk_to_dict(self.risk_assessment.landslide),
            'erosion': risk_to_dict(self.risk_assessment.erosion),
            'seismic': risk_to_dict(self.risk_assessment.seismic),
            'drought': risk_to_dict(self.risk_assessment.drought),
            'wildfire': risk_to_dict(self.risk_assessment.wildfire),
            'subsidence': risk_to_dict(self.risk_assessment.subsidence),
            'overall': {
                'level': self.risk_assessment.overall_level.name.lower(),
                'average_severity': self.risk_assessment.average_severity,
                'high_risk_count': self.risk_assessment.high_risk_count,
                'medium_risk_count': self.risk_assessment.medium_risk_count
            },
            'summary': self.risk_assessment.summary,
            'mitigation': self.risk_assessment.mitigation
        }
    
    # ========== VALIDATION ==========
    
    def validate(self) -> List[str]:
        """
        Validate result integrity
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.metadata.analysis_id:
            errors.append("Missing analysis_id")
        
        if not self.boundary:
            errors.append("Missing boundary data")
        
        if not self.features:
            errors.append("Missing features")
        
        if self.risk_assessment is None:
            errors.append("Missing risk_assessment")
        
        if not 0 <= self.overall_score <= 10:
            errors.append(f"Invalid overall_score: {self.overall_score}")
        
        if not 0 <= self.confidence_level <= 1:
            errors.append(f"Invalid confidence_level: {self.confidence_level}")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if result is valid"""
        return len(self.validate()) == 0
    
    # ========== COMPARISON ==========
    
    def compare_to(self, other: 'AnalysisResult') -> Dict:
        """
        Compare this result to another
        
        Useful for tracking changes over time
        """
        return {
            'score_diff': self.overall_score - other.overall_score,
            'confidence_diff': self.confidence_level - other.confidence_level,
            'risk_level_changed': self.overall_risk_level != other.overall_risk_level,
            'high_risk_diff': self.high_risk_count - other.high_risk_count,
            'time_diff_seconds': (
                datetime.fromisoformat(self.timestamp) - 
                datetime.fromisoformat(other.timestamp)
            ).total_seconds()
        }
