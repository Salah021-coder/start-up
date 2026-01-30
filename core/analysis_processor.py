# ============================================================================
# FILE: core/analysis_processor.py
# Main Analysis Pipeline Orchestrator
# ============================================================================

from typing import Dict, Optional, Callable, List
import logging
from datetime import datetime
import uuid

from core.boundary_manager import BoundaryManager
from core.features.terrain import TerrainExtractor
from core.features.environmental import EnvironmentalExtractor
from core.features.infrastructure import InfrastructureExtractor
from core.criteria_engine import CriteriaEngine
from core.suitability.ahp_engine import AHPEngine
from core.recommendation.usage_recommender import UsageRecommender
from core.risk import RiskEngine, RiskSignal
from core.risk.signal_adapter import FeatureToSignalAdapter
from utils.ee_manager import EarthEngineManager

logger = logging.getLogger(__name__)


class AnalysisProcessor:
    """
    Main analysis pipeline orchestrator
    
    RESPONSIBILITIES:
    - Coordinate all analysis stages
    - Manage data flow between components
    - Handle errors gracefully
    - Report progress
    - Return complete analysis results
    
    WORKFLOW:
    1. Validate boundary
    2. Extract terrain features (Earth Engine)
    3. Extract environmental features (Earth Engine)
    4. Extract infrastructure features (OpenStreetMap)
    5. Assess comprehensive risks
    6. Auto-select evaluation criteria
    7. Calculate AHP suitability scores
    8. Generate land-use recommendations
    9. Compile final results
    
    DOES NOT:
    - Store results (caller's responsibility)
    - Make UI decisions
    - Provide fallback data silently
    """
    
    def __init__(self):
        """Initialize analysis processor"""
        
        # Check Earth Engine availability
        self.ee_available = EarthEngineManager.is_available()
        
        if not self.ee_available:
            logger.warning("Earth Engine not available - analysis will be limited")
        
        # Initialize all components
        self.boundary_manager = BoundaryManager()
        
        # Feature extractors
        if self.ee_available:
            self.terrain_extractor = TerrainExtractor()
            self.env_extractor = EnvironmentalExtractor()
        else:
            self.terrain_extractor = None
            self.env_extractor = None
        
        self.infra_extractor = InfrastructureExtractor(use_real_osm=True)
        
        # Analysis engines
        self.criteria_engine = CriteriaEngine()
        self.ahp_engine = AHPEngine()
        self.recommender = UsageRecommender()
        self.risk_engine = RiskEngine()
        self.signal_adapter = FeatureToSignalAdapter()
        
        logger.info(
            f"AnalysisProcessor initialized (EE: {'available' if self.ee_available else 'unavailable'})"
        )
    
    def run_analysis(
        self,
        boundary_data: Dict,
        criteria: Optional[Dict] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict:
        """
        Run complete land analysis
        
        Args:
            boundary_data: Boundary geometry and metadata
            criteria: Optional pre-selected criteria (auto-selected if None)
            progress_callback: Optional callback(message, percent)
            
        Returns:
            Complete analysis results dict
            
        Raises:
            ValueError: If boundary invalid
            RuntimeError: If critical stage fails
        """
        analysis_id = self._generate_analysis_id()
        start_time = datetime.now()
        
        logger.info(f"Starting analysis {analysis_id}")
        
        try:
            # === STAGE 1: VALIDATE BOUNDARY ===
            self._update_progress(progress_callback, "Validating boundary...", 5)
            
            validated_boundary = self._validate_boundary(boundary_data)
            
            logger.info(
                f"Boundary validated: {validated_boundary['area_km2']:.2f} km²"
            )
            
            # === STAGE 2: EXTRACT TERRAIN FEATURES ===
            self._update_progress(progress_callback, "Extracting terrain features...", 15)
            
            terrain_features = self._extract_terrain(validated_boundary, progress_callback)
            
            # === STAGE 3: EXTRACT ENVIRONMENTAL FEATURES ===
            self._update_progress(progress_callback, "Extracting environmental features...", 30)
            
            env_features = self._extract_environmental(
                validated_boundary,
                terrain_features,
                progress_callback
            )
            
            # === STAGE 4: EXTRACT INFRASTRUCTURE FEATURES ===
            self._update_progress(progress_callback, "Extracting infrastructure features...", 45)
            
            infra_features = self._extract_infrastructure(validated_boundary, progress_callback)
            
            # === COMPILE FEATURES ===
            all_features = {
                'terrain': terrain_features,
                'environmental': env_features,
                'infrastructure': infra_features,
                'boundary': validated_boundary
            }
            
            logger.info("All features extracted successfully")
            
            # === STAGE 5: ASSESS RISKS ===
            self._update_progress(progress_callback, "Assessing risks...", 60)
            
            risk_result = self._assess_risks(all_features)
            
            # === STAGE 6: SELECT CRITERIA (if not provided) ===
            if criteria is None:
                self._update_progress(progress_callback, "Auto-selecting criteria...", 70)
                
                criteria_result = self.criteria_engine.auto_select_criteria(
                    validated_boundary,
                    all_features
                )
                criteria = criteria_result['criteria']
                
                logger.info(f"Criteria auto-selected: {criteria_result['land_use_hint']}")
            else:
                logger.info("Using provided criteria")
                criteria_result = {
                    'criteria': criteria,
                    'land_use_hint': 'custom',
                    'reasoning': ['User-provided criteria']
                }
            
            # === STAGE 7: CALCULATE SUITABILITY (AHP) ===
            self._update_progress(progress_callback, "Calculating suitability scores...", 80)
            
            suitability_result = self.ahp_engine.calculate_suitability(
                all_features,
                criteria
            )
            
            logger.info(f"AHP suitability: {suitability_result['overall_score']:.2f}/10")
            
            # === STAGE 8: GENERATE RECOMMENDATIONS ===
            self._update_progress(progress_callback, "Generating recommendations...", 90)
            
            recommendations = self.recommender.generate_recommendations(
                all_features,
                risk_result,
                suitability_result,
                top_n=10
            )
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            
            # === STAGE 9: COMPILE FINAL RESULTS ===
            self._update_progress(progress_callback, "Compiling results...", 95)
            
            final_results = self._compile_results(
                analysis_id=analysis_id,
                start_time=start_time,
                boundary=validated_boundary,
                features=all_features,
                criteria_result=criteria_result,
                risk_result=risk_result,
                suitability_result=suitability_result,
                recommendations=recommendations
            )
            
            self._update_progress(progress_callback, "Analysis complete!", 100)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Analysis {analysis_id} completed in {duration:.2f}s, "
                f"overall score: {final_results['overall_score']:.2f}/10"
            )
            
            return final_results
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}", exc_info=True)
            raise
    
    def _validate_boundary(self, boundary_data: Dict) -> Dict:
        """
        Validate and standardize boundary data
        
        Args:
            boundary_data: Raw boundary data
            
        Returns:
            Validated boundary with all required fields
            
        Raises:
            ValueError: If boundary invalid
        """
        # Check if already processed by BoundaryManager
        if 'geometry' in boundary_data and 'area_m2' in boundary_data:
            # Already validated
            validation_result = self.boundary_manager.validate_boundary(boundary_data)
            
            if not validation_result['is_valid']:
                raise ValueError(f"Boundary validation failed: {validation_result['errors']}")
            
            return boundary_data
        
        # Need to create boundary from raw data
        if 'coordinates' in boundary_data:
            coords = boundary_data['coordinates']
            return self.boundary_manager.create_from_coordinates(coords)
        
        elif 'geojson' in boundary_data:
            return self.boundary_manager.import_from_geojson_dict(boundary_data['geojson'])
        
        else:
            raise ValueError(
                "Boundary data must contain either 'geometry' + 'area_m2' "
                "or 'coordinates' or 'geojson'"
            )
    
    def _extract_terrain(
        self,
        boundary: Dict,
        progress_callback: Optional[Callable]
    ) -> Dict:
        """
        Extract terrain features
        
        Raises:
            RuntimeError: If Earth Engine unavailable or extraction fails
        """
        if not self.ee_available or not self.terrain_extractor:
            raise RuntimeError(
                "Earth Engine required for terrain extraction. "
                "Please configure GEE credentials."
            )
        
        ee_geometry = boundary.get('ee_geometry')
        if not ee_geometry:
            raise RuntimeError("Boundary missing Earth Engine geometry")
        
        try:
            terrain = self.terrain_extractor.extract(ee_geometry)
            
            logger.info(
                f"Terrain extracted: slope {terrain['slope_avg']:.1f}°, "
                f"elevation {terrain['elevation_avg']:.0f}m"
            )
            
            return terrain
            
        except Exception as e:
            logger.error(f"Terrain extraction failed: {e}")
            raise RuntimeError(f"Failed to extract terrain features: {e}")
    
    def _extract_environmental(
        self,
        boundary: Dict,
        terrain: Dict,
        progress_callback: Optional[Callable]
    ) -> Dict:
        """
        Extract environmental features
        
        Falls back to minimal data if extraction fails (logged)
        """
        if not self.ee_available or not self.env_extractor:
            logger.warning("Earth Engine unavailable - using minimal environmental data")
            return self._get_minimal_environmental()
        
        ee_geometry = boundary.get('ee_geometry')
        if not ee_geometry:
            logger.warning("No EE geometry - using minimal environmental data")
            return self._get_minimal_environmental()
        
        try:
            env = self.env_extractor.extract(ee_geometry, terrain)
            
            logger.info(
                f"Environmental extracted: NDVI {env['ndvi_avg']:.2f}, "
                f"land cover: {env['dominant_cover']}"
            )
            
            return env
            
        except Exception as e:
            logger.warning(f"Environmental extraction failed: {e}, using minimal data")
            return self._get_minimal_environmental()
    
    def _extract_infrastructure(
        self,
        boundary: Dict,
        progress_callback: Optional[Callable]
    ) -> Dict:
        """
        Extract infrastructure features
        
        Args:
            boundary: Validated boundary
            progress_callback: Progress callback
            
        Returns:
            Infrastructure features
            
        Raises:
            RuntimeError: If extraction fails critically
        """
        centroid = boundary.get('centroid')
        geometry = boundary.get('geometry')
        ee_geometry = boundary.get('ee_geometry')
        
        if not centroid:
            raise RuntimeError("Boundary missing centroid")
        
        try:
            infra = self.infra_extractor.extract(
                ee_geometry=ee_geometry,
                centroid=centroid,
                geometry=geometry
            )
            
            logger.info(
                f"Infrastructure extracted: {infra['urbanization_level']}, "
                f"road: {infra['nearest_road_distance']:.0f}m, "
                f"quality: {infra['data_quality']}"
            )
            
            return infra
            
        except Exception as e:
            logger.error(f"Infrastructure extraction failed: {e}")
            raise RuntimeError(f"Failed to extract infrastructure features: {e}")
    
    def _assess_risks(self, features: Dict):
        """
        Assess all risks using centralized risk engine
        
        Args:
            features: All extracted features
            
        Returns:
            ComprehensiveRiskResult
        """
        try:
            # Convert features to risk signals
            signals = self.signal_adapter.convert_all_features(features)
            location = self.signal_adapter.extract_location(features)
            
            logger.info(f"Converted {len(signals)} signals for risk assessment")
            
            # Run comprehensive risk assessment
            risk_result = self.risk_engine.assess_all_risks(
                signals=signals,
                location=location
            )
            
            logger.info(
                f"Risk assessment: {risk_result.overall_level.name}, "
                f"high risks: {risk_result.high_risk_count}"
            )
            
            return risk_result
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}", exc_info=True)
            raise RuntimeError(f"Risk assessment failed: {e}")
    
    def _compile_results(
        self,
        analysis_id: str,
        start_time: datetime,
        boundary: Dict,
        features: Dict,
        criteria_result: Dict,
        risk_result,
        suitability_result: Dict,
        recommendations: List[Dict]
    ) -> Dict:
        """
        Compile all results into final output
        
        This creates the complete analysis result that UI will consume
        
        Returns:
            Complete analysis results dictionary
        """
        duration = (datetime.now() - start_time).total_seconds()
        
        # Calculate overall score (weighted combination)
        overall_score = suitability_result['overall_score']
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(features, risk_result, suitability_result)
        
        # Generate key insights
        insights = self._generate_insights(
            features,
            risk_result,
            suitability_result,
            recommendations
        )
        
        # Convert risk result to legacy format for compatibility
        comprehensive_risks = self._risk_to_legacy_format(risk_result)
        
        # Compile final result
        results = {
            # Metadata
            'analysis_id': analysis_id,
            'timestamp': start_time.isoformat(),
            'duration_seconds': duration,
            
            # Boundary
            'boundary': boundary,
            
            # Features (all extracted data)
            'features': features,
            
            # Overall scores
            'overall_score': round(overall_score, 2),
            'confidence_level': confidence,
            
            # Detailed results
            'criteria': criteria_result,
            'suitability': suitability_result,
            'recommendations': recommendations,
            
            # Risk assessment (in features for backwards compatibility)
            'risk_assessment': {
                'overall_level': risk_result.overall_level.name.lower().replace('_', ' '),
                'average_severity': risk_result.average_severity,
                'high_risk_count': risk_result.high_risk_count,
                'medium_risk_count': risk_result.medium_risk_count,
                'summary': risk_result.summary,
                'mitigation': risk_result.mitigation
            },
            
            # Key insights
            'key_insights': insights,
            
            # Data quality info
            'data_sources': {
                'terrain': features['terrain'].get('data_quality', 'unknown'),
                'environmental': features['environmental'].get('data_quality', 'unknown'),
                'infrastructure': features['infrastructure'].get('data_quality', 'unknown'),
                'earth_engine': self.ee_available,
                'risk_assessment': 'comprehensive'
            },
            
            # Final scores breakdown
            'final_scores': {
                'overall_score': overall_score,
                'ahp_score': suitability_result['overall_score'],
                'confidence': confidence
            }
        }
        
        # Add comprehensive risks to environmental features (for UI compatibility)
        features['environmental']['comprehensive_risks'] = comprehensive_risks
        
        return results
    
    def _calculate_confidence(
        self,
        features: Dict,
        risk_result,
        suitability_result: Dict
    ) -> float:
        """
        Calculate overall confidence in analysis results
        
        Based on:
        - Data quality
        - Feature completeness
        - Risk assessment confidence
        - AHP consistency
        
        Returns:
            Confidence level (0.0 to 1.0)
        """
        confidence_factors = []
        
        # Data quality factors
        terrain_quality = features['terrain'].get('data_quality', 'unknown')
        if terrain_quality == 'gee':
            confidence_factors.append(0.95)
        else:
            confidence_factors.append(0.60)
        
        infra_quality = features['infrastructure'].get('data_quality', 'unknown')
        if infra_quality == 'real_osm':
            confidence_factors.append(0.90)
        elif infra_quality == 'estimated':
            confidence_factors.append(0.60)
        else:
            confidence_factors.append(0.70)
        
        # AHP consistency
        if suitability_result.get('is_consistent', True):
            confidence_factors.append(0.85)
        else:
            confidence_factors.append(0.70)
        
        # Risk assessment confidence (average of all risk confidences)
        risk_confidences = [
            risk_result.flood.confidence,
            risk_result.landslide.confidence,
            risk_result.erosion.confidence,
            risk_result.seismic.confidence,
            risk_result.drought.confidence,
            risk_result.wildfire.confidence,
            risk_result.subsidence.confidence
        ]
        avg_risk_confidence = sum(risk_confidences) / len(risk_confidences)
        confidence_factors.append(avg_risk_confidence)
        
        # Overall confidence is average of all factors
        overall = sum(confidence_factors) / len(confidence_factors)
        
        return round(overall, 2)
    
    def _generate_insights(
        self,
        features: Dict,
        risk_result,
        suitability_result: Dict,
        recommendations: List[Dict]
    ) -> Dict:
        """
        Generate key insights from analysis
        
        Returns:
            Dict with categorized insights
        """
        insights = {
            'strengths': [],
            'concerns': [],
            'opportunities': [],
            'development_potential': ''
        }
        
        terrain = features['terrain']
        env = features['environmental']
        infra = features['infrastructure']
        
        # === STRENGTHS ===
        
        # Terrain strengths
        if terrain['slope_avg'] < 5:
            insights['strengths'].append(
                f"Gentle terrain ({terrain['slope_avg']:.1f}° slope) ideal for construction"
            )
        
        if terrain['buildability_score'] >= 8:
            insights['strengths'].append(
                f"Excellent buildability ({terrain['buildability_class']})"
            )
        
        # Infrastructure strengths
        road_dist = infra['nearest_road_distance']
        if road_dist < 500:
            insights['strengths'].append(
                f"Excellent road access ({road_dist:.0f}m to nearest road)"
            )
        
        if infra['utilities_available'] >= 4:
            insights['strengths'].append(
                f"Good utility availability ({infra['utilities_available']}/5 utilities)"
            )
        
        # Environmental strengths
        if env['ndvi_avg'] > 0.6:
            insights['strengths'].append(
                f"Healthy vegetation (NDVI {env['ndvi_avg']:.2f})"
            )
        
        # Risk strengths
        if risk_result.high_risk_count == 0:
            insights['strengths'].append(
                "No high-severity environmental risks identified"
            )
        
        # === CONCERNS ===
        
        # Risk concerns
        if risk_result.high_risk_count > 0:
            insights['concerns'].append(
                f"⚠️ {risk_result.high_risk_count} high-severity risk(s) require mitigation"
            )
        
        # Terrain concerns
        if terrain['slope_avg'] > 15:
            insights['concerns'].append(
                f"Steep terrain ({terrain['slope_avg']:.1f}°) increases construction costs"
            )
        
        # Infrastructure concerns
        if road_dist > 2000:
            insights['concerns'].append(
                f"Limited road access ({road_dist/1000:.1f}km from nearest road)"
            )
        
        if infra['utilities_available'] < 2:
            insights['concerns'].append(
                f"Limited utility availability ({infra['utilities_available']}/5 utilities)"
            )
        
        # === OPPORTUNITIES ===
        
        # High suitability
        if suitability_result['overall_score'] > 8:
            insights['opportunities'].append(
                "Exceptional suitability - strong development potential"
            )
        
        # Development pressure
        dev_pressure = infra.get('development_pressure', 'medium')
        if dev_pressure in ['high', 'very_high']:
            insights['opportunities'].append(
                f"{dev_pressure.replace('_', ' ').title()} development pressure indicates market demand"
            )
        
        # Agricultural potential
        if env['ndvi_avg'] > 0.6 and terrain['slope_avg'] < 12:
            insights['opportunities'].append(
                "Good agricultural potential with fertile soil indicators"
            )
        
        # === DEVELOPMENT POTENTIAL ===
        
        score = suitability_result['overall_score']
        high_risks = risk_result.high_risk_count
        
        if score > 8 and high_risks == 0:
            potential = "Exceptional development potential with minimal constraints"
        elif score > 7 and high_risks <= 1:
            potential = "Strong development potential with manageable considerations"
        elif score > 6:
            potential = "Good development potential - careful planning recommended"
        elif score > 5:
            potential = "Moderate potential - thorough site assessment advised"
        else:
            potential = "Limited potential - significant constraints present"
        
        insights['development_potential'] = potential
        
        return insights
    
    def _risk_to_legacy_format(self, risk_result) -> Dict:
        """
        Convert new RiskResult to legacy comprehensive_risks format
        
        For UI backwards compatibility
        """
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
            'flood': risk_to_dict(risk_result.flood),
            'landslide': risk_to_dict(risk_result.landslide),
            'erosion': risk_to_dict(risk_result.erosion),
            'seismic': risk_to_dict(risk_result.seismic),
            'drought': risk_to_dict(risk_result.drought),
            'wildfire': risk_to_dict(risk_result.wildfire),
            'subsidence': risk_to_dict(risk_result.subsidence),
            'overall': {
                'level': risk_result.overall_level.name.lower(),
                'average_severity': risk_result.average_severity,
                'high_risk_count': risk_result.high_risk_count,
                'medium_risk_count': risk_result.medium_risk_count,
                'total_risks_assessed': 7
            },
            'summary': risk_result.summary,
            'mitigation': risk_result.mitigation
        }
    
    def _get_minimal_environmental(self) -> Dict:
        """
        Minimal environmental data when extraction fails
        
        Logged as fallback, not silent
        """
        logger.warning("Using minimal environmental data (extraction unavailable)")
        
        return {
            'ndvi_avg': 0.5,
            'ndvi_min': 0.2,
            'ndvi_max': 0.8,
            'ndvi_std': 0.1,
            'vegetation_health': 'moderate',
            'dominant_cover': 'unknown',
            'land_cover_distribution': {},
            'land_cover_diversity': 0.0,
            'water_occurrence_avg': 0.0,
            'water_occurrence_max': 0.0,
            'permanent_water_percent': 0.0,
            'green_space_percent': 50.0,
            'environmental_score': 5.0,
            'data_quality': 'minimal',
            'notes': 'Environmental data unavailable - using conservative estimates'
        }
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique = str(uuid.uuid4())[:8]
        return f"LAND_{timestamp}_{unique}"
    
    def _update_progress(
        self,
        callback: Optional[Callable],
        message: str,
        percent: int
    ):
        """Update progress if callback provided"""
        if callback:
            try:
                callback(message, percent)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
        
        logger.debug(f"Progress: {percent}% - {message}")
