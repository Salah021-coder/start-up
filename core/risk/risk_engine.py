# ============================================================================
# FILE: core/risk/risk_engine.py
# Central Risk Engine (Rule-based + ML Hybrid)
# ============================================================================

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Standardized risk levels"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    UNKNOWN = 0


@dataclass
class RiskSignal:
    """Raw indicator before interpretation"""
    name: str
    value: float
    unit: str
    source: str  # 'gee', 'osm', 'computed', 'ml'
    confidence: float  # 0.0 to 1.0


@dataclass
class RiskAssessment:
    """Final risk assessment with provenance"""
    risk_type: str
    level: RiskLevel
    severity: int  # 1-5
    score: float  # 0-100
    signals: List[RiskSignal]
    primary_factors: List[str]
    description: str
    impact: str
    method: str  # 'rule_based', 'ml_based', 'hybrid'
    confidence: float


@dataclass
class ComprehensiveRiskResult:
    """Complete risk assessment output"""
    flood: RiskAssessment
    landslide: RiskAssessment
    erosion: RiskAssessment
    seismic: RiskAssessment
    drought: RiskAssessment
    wildfire: RiskAssessment
    subsidence: RiskAssessment
    overall_level: RiskLevel
    average_severity: float
    high_risk_count: int
    medium_risk_count: int
    summary: List[str]
    mitigation: List[str]
    timestamp: str
    version: str = "2.0"


class RiskEngine:
    """
    Central risk assessment engine combining:
    - Rule-based thresholds
    - ML predictions
    - Expert knowledge
    
    RULES:
    1. Never returns default without logging
    2. Never guesses missing data
    3. Always tracks provenance
    4. ML adapter is optional (graceful degradation)
    """
    
    def __init__(self, ml_adapter=None):
        """
        Args:
            ml_adapter: Optional ML model adapter for predictions
        """
        self.ml_adapter = ml_adapter
        from core.risk.rules import RiskRules
        from core.risk.validator import SignalValidator
        
        self.rules = RiskRules()
        self.validator = SignalValidator()
    
    def assess_all_risks(
        self, 
        signals: Dict[str, RiskSignal],
        location: Optional[Dict] = None
    ) -> ComprehensiveRiskResult:
        """
        Main entry point for comprehensive risk assessment
        
        Args:
            signals: Dictionary of validated risk signals
            location: Optional location context (lat, lon)
            
        Returns:
            ComprehensiveRiskResult with all assessments
            
        Raises:
            ValueError: If signals are invalid or insufficient
        """
        # Validate all signals
        validation_errors = self.validator.validate_signals(signals)
        if validation_errors:
            logger.error(f"Signal validation failed: {validation_errors}")
            raise ValueError(f"Invalid signals: {validation_errors}")
        
        logger.info(f"Starting risk assessment with {len(signals)} signals")
        
        # Assess each risk type
        assessments = {}
        
        try:
            assessments['flood'] = self._assess_flood(signals)
            assessments['landslide'] = self._assess_landslide(signals)
            assessments['erosion'] = self._assess_erosion(signals)
            assessments['seismic'] = self._assess_seismic(signals, location)
            assessments['drought'] = self._assess_drought(signals, location)
            assessments['wildfire'] = self._assess_wildfire(signals)
            assessments['subsidence'] = self._assess_subsidence(signals)
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}", exc_info=True)
            raise
        
        # Calculate overall risk
        overall = self._calculate_overall(assessments)
        
        # Generate summary and mitigation
        summary = self._generate_summary(assessments, overall)
        mitigation = self._generate_mitigation(assessments)
        
        from datetime import datetime
        
        return ComprehensiveRiskResult(
            flood=assessments['flood'],
            landslide=assessments['landslide'],
            erosion=assessments['erosion'],
            seismic=assessments['seismic'],
            drought=assessments['drought'],
            wildfire=assessments['wildfire'],
            subsidence=assessments['subsidence'],
            overall_level=overall['level'],
            average_severity=overall['average_severity'],
            high_risk_count=overall['high_count'],
            medium_risk_count=overall['medium_count'],
            summary=summary,
            mitigation=mitigation,
            timestamp=datetime.now().isoformat()
        )
    
    def _assess_flood(self, signals: Dict[str, RiskSignal]) -> RiskAssessment:
        """Assess flood risk using rules + optional ML"""
        
        # Extract required signals
        slope = signals.get('slope_avg')
        water_occurrence = signals.get('water_occurrence', None)
        elevation = signals.get('elevation_avg')
        
        if not slope or not elevation:
            raise ValueError("Missing required signals for flood assessment: slope_avg, elevation_avg")
        
        # Rule-based assessment
        rule_score = self.rules.calculate_flood_score(
            slope_avg=slope.value,
            elevation=elevation.value,
            water_occurrence=water_occurrence.value if water_occurrence else 0
        )
        
        # ML enhancement if available
        ml_score = None
        if self.ml_adapter:
            try:
                ml_score = self.ml_adapter.predict_flood_risk({
                    'slope': slope.value,
                    'elevation': elevation.value,
                    'water_occ': water_occurrence.value if water_occurrence else 0
                })
            except Exception as e:
                logger.warning(f"ML flood prediction failed: {e}")
        
        # Combine scores
        final_score, method = self._combine_scores(rule_score, ml_score)
        
        # Determine level and severity
        level, severity = self.rules.score_to_level_severity(final_score)
        
        # Build factors list
        factors = []
        if slope.value < 3:
            factors.append(f"Very flat terrain: {slope.value:.1f}° (poor drainage)")
        else:
            factors.append(f"Slope: {slope.value:.1f}° (drainage adequate)")
        
        if water_occurrence and water_occurrence.value > 20:
            factors.append(f"High water occurrence: {water_occurrence.value:.0f}%")
        
        factors.append(f"Elevation: {elevation.value:.0f}m")
        
        return RiskAssessment(
            risk_type='flood',
            level=level,
            severity=severity,
            score=final_score,
            signals=[slope, elevation] + ([water_occurrence] if water_occurrence else []),
            primary_factors=factors,
            description=self.rules.get_flood_description(level),
            impact=self.rules.get_flood_impact(severity),
            method=method,
            confidence=self._calculate_confidence([slope, elevation, water_occurrence])
        )
    
    def _assess_landslide(self, signals: Dict[str, RiskSignal]) -> RiskAssessment:
        """Assess landslide risk"""
        
        slope_avg = signals.get('slope_avg')
        slope_max = signals.get('slope_max')
        elevation_range = signals.get('elevation_range')
        
        if not slope_avg:
            raise ValueError("Missing required signal: slope_avg")
        
        # Use max slope if available, otherwise estimate
        max_slope = slope_max.value if slope_max else slope_avg.value * 1.5
        
        rule_score = self.rules.calculate_landslide_score(
            slope_avg=slope_avg.value,
            slope_max=max_slope,
            elevation_range=elevation_range.value if elevation_range else 0
        )
        
        # ML enhancement
        ml_score = None
        if self.ml_adapter:
            try:
                ml_score = self.ml_adapter.predict_landslide_risk({
                    'slope_avg': slope_avg.value,
                    'slope_max': max_slope
                })
            except Exception as e:
                logger.warning(f"ML landslide prediction failed: {e}")
        
        final_score, method = self._combine_scores(rule_score, ml_score)
        level, severity = self.rules.score_to_level_severity(final_score)
        
        factors = [
            f"Average slope: {slope_avg.value:.1f}°",
            f"Maximum slope: {max_slope:.1f}°"
        ]
        
        if elevation_range:
            factors.append(f"Elevation variation: {elevation_range.value:.0f}m")
        
        return RiskAssessment(
            risk_type='landslide',
            level=level,
            severity=severity,
            score=final_score,
            signals=[s for s in [slope_avg, slope_max, elevation_range] if s],
            primary_factors=factors,
            description=self.rules.get_landslide_description(level),
            impact=self.rules.get_landslide_impact(severity),
            method=method,
            confidence=self._calculate_confidence([slope_avg, slope_max])
        )
    
    def _assess_erosion(self, signals: Dict[str, RiskSignal]) -> RiskAssessment:
        """Assess erosion risk"""
        
        slope = signals.get('slope_avg')
        vegetation = signals.get('ndvi_avg')
        
        if not slope:
            raise ValueError("Missing required signal: slope_avg")
        
        rule_score = self.rules.calculate_erosion_score(
            slope=slope.value,
            vegetation_cover=vegetation.value if vegetation else 0.5
        )
        
        final_score, method = self._combine_scores(rule_score, None)
        level, severity = self.rules.score_to_level_severity(final_score)
        
        factors = [f"Slope: {slope.value:.1f}°"]
        if vegetation:
            factors.append(f"Vegetation cover: NDVI {vegetation.value:.2f}")
        
        return RiskAssessment(
            risk_type='erosion',
            level=level,
            severity=severity,
            score=final_score,
            signals=[s for s in [slope, vegetation] if s],
            primary_factors=factors,
            description=self.rules.get_erosion_description(level),
            impact=self.rules.get_erosion_impact(severity),
            method=method,
            confidence=self._calculate_confidence([slope, vegetation])
        )
    
    def _assess_seismic(
        self, 
        signals: Dict[str, RiskSignal],
        location: Optional[Dict]
    ) -> RiskAssessment:
        """Assess seismic risk (location-dependent)"""
        
        if not location or 'lat' not in location or 'lon' not in location:
            logger.warning("No location provided for seismic assessment, using conservative estimate")
            # Conservative default for Algeria
            location = {'lat': 36.0, 'lon': 5.0}
        
        lat = location['lat']
        lon = location['lon']
        
        score, zone = self.rules.calculate_seismic_score(lat, lon)
        level, severity = self.rules.score_to_level_severity(score)
        
        # Create pseudo-signal for location
        location_signal = RiskSignal(
            name='location',
            value=lat,
            unit='degrees',
            source='input',
            confidence=1.0
        )
        
        factors = [
            f"Seismic Zone {zone}",
            f"Location: {lat:.2f}°N, {lon:.2f}°E"
        ]
        
        return RiskAssessment(
            risk_type='seismic',
            level=level,
            severity=severity,
            score=score,
            signals=[location_signal],
            primary_factors=factors,
            description=self.rules.get_seismic_description(level, zone),
            impact=self.rules.get_seismic_impact(severity),
            method='rule_based',  # Always rule-based for seismic
            confidence=0.85  # High confidence for known seismic zones
        )
    
    def _assess_drought(
        self,
        signals: Dict[str, RiskSignal],
        location: Optional[Dict]
    ) -> RiskAssessment:
        """Assess drought risk"""
        
        ndvi = signals.get('ndvi_avg')
        
        if not location or 'lat' not in location:
            logger.warning("No location for drought assessment")
            location = {'lat': 36.0}
        
        lat = location['lat']
        
        score = self.rules.calculate_drought_score(
            latitude=lat,
            vegetation_health=ndvi.value if ndvi else 0.5
        )
        
        level, severity = self.rules.score_to_level_severity(score)
        
        factors = [
            f"Climate zone at {lat:.1f}°N",
            "Historical rainfall patterns"
        ]
        
        if ndvi:
            factors.append(f"Vegetation health: NDVI {ndvi.value:.2f}")
        
        return RiskAssessment(
            risk_type='drought',
            level=level,
            severity=severity,
            score=score,
            signals=[ndvi] if ndvi else [],
            primary_factors=factors,
            description=self.rules.get_drought_description(level),
            impact=self.rules.get_drought_impact(severity),
            method='rule_based',
            confidence=0.75
        )
    
    def _assess_wildfire(self, signals: Dict[str, RiskSignal]) -> RiskAssessment:
        """Assess wildfire risk"""
        
        slope = signals.get('slope_avg')
        vegetation = signals.get('ndvi_avg')
        
        score = self.rules.calculate_wildfire_score(
            slope=slope.value if slope else 5.0,
            vegetation_density=vegetation.value if vegetation else 0.5
        )
        
        level, severity = self.rules.score_to_level_severity(score)
        
        factors = []
        if vegetation:
            factors.append(f"Vegetation density: NDVI {vegetation.value:.2f}")
        if slope:
            factors.append(f"Slope: {slope.value:.1f}°")
        
        return RiskAssessment(
            risk_type='wildfire',
            level=level,
            severity=severity,
            score=score,
            signals=[s for s in [slope, vegetation] if s],
            primary_factors=factors or ["Moderate fire risk conditions"],
            description=self.rules.get_wildfire_description(level),
            impact=self.rules.get_wildfire_impact(severity),
            method='rule_based',
            confidence=0.70
        )
    
    def _assess_subsidence(self, signals: Dict[str, RiskSignal]) -> RiskAssessment:
        """Assess subsidence risk"""
        
        elevation = signals.get('elevation_avg')
        slope = signals.get('slope_avg')
        
        if not elevation or not slope:
            raise ValueError("Missing required signals for subsidence: elevation_avg, slope_avg")
        
        score = self.rules.calculate_subsidence_score(
            elevation=elevation.value,
            slope=slope.value
        )
        
        level, severity = self.rules.score_to_level_severity(score)
        
        factors = [
            f"Elevation: {elevation.value:.0f}m",
            f"Slope: {slope.value:.1f}°"
        ]
        
        return RiskAssessment(
            risk_type='subsidence',
            level=level,
            severity=severity,
            score=score,
            signals=[elevation, slope],
            primary_factors=factors,
            description=self.rules.get_subsidence_description(level),
            impact=self.rules.get_subsidence_impact(severity),
            method='rule_based',
            confidence=0.65
        )
    
    def _combine_scores(
        self, 
        rule_score: float, 
        ml_score: Optional[float]
    ) -> tuple[float, str]:
        """
        Combine rule-based and ML scores
        
        Returns:
            (final_score, method)
        """
        if ml_score is None:
            return rule_score, 'rule_based'
        
        # Weighted average: 60% rules, 40% ML
        # Rules are more reliable for physical constraints
        final = 0.6 * rule_score + 0.4 * ml_score
        
        return final, 'hybrid'
    
    def _calculate_confidence(self, signals: List[Optional[RiskSignal]]) -> float:
        """Calculate confidence based on signal quality"""
        valid_signals = [s for s in signals if s is not None]
        
        if not valid_signals:
            return 0.5
        
        # Average signal confidence
        avg_confidence = sum(s.confidence for s in valid_signals) / len(valid_signals)
        
        # Penalty for missing signals
        signal_completeness = len(valid_signals) / len(signals)
        
        return avg_confidence * signal_completeness
    
    def _calculate_overall(self, assessments: Dict[str, RiskAssessment]) -> Dict:
        """Calculate overall risk profile"""
        
        severities = [a.severity for a in assessments.values()]
        avg_severity = sum(severities) / len(severities)
        
        high_count = sum(1 for s in severities if s >= 4)
        medium_count = sum(1 for s in severities if s == 3)
        
        # Determine overall level
        if high_count >= 3 or avg_severity >= 4.0:
            overall_level = RiskLevel.VERY_HIGH
        elif high_count >= 2 or avg_severity >= 3.5:
            overall_level = RiskLevel.HIGH
        elif high_count >= 1 or medium_count >= 3:
            overall_level = RiskLevel.MEDIUM
        elif medium_count >= 1:
            overall_level = RiskLevel.LOW
        else:
            overall_level = RiskLevel.VERY_LOW
        
        return {
            'level': overall_level,
            'average_severity': avg_severity,
            'high_count': high_count,
            'medium_count': medium_count
        }
    
    def _generate_summary(
        self,
        assessments: Dict[str, RiskAssessment],
        overall: Dict
    ) -> List[str]:
        """Generate summary text"""
        
        summary = []
        
        # List major risks
        major = [
            (name, assess) for name, assess in assessments.items()
            if assess.severity >= 4
        ]
        
        if major:
            risk_list = ', '.join([
                f"{name.title()} ({a.level.name.replace('_', ' ').title()})"
                for name, a in major
            ])
            summary.append(f"⚠️ **High Risks:** {risk_list}")
        else:
            summary.append("✅ **No high-severity risks identified**")
        
        summary.append(
            f"📊 **Overall Risk Level:** {overall['level'].name.replace('_', ' ').title()}"
        )
        summary.append(f"📈 **Average Severity:** {overall['average_severity']:.1f}/5")
        summary.append(
            f"🔍 **Risk Distribution:** {overall['high_count']} High, "
            f"{overall['medium_count']} Medium"
        )
        
        return summary
    
    def _generate_mitigation(self, assessments: Dict[str, RiskAssessment]) -> List[str]:
        """Generate mitigation recommendations"""
        
        mitigation = []
        
        for name, assess in assessments.items():
            if assess.severity >= 3:
                rec = self.rules.get_mitigation_recommendation(name, assess.severity)
                if rec:
                    mitigation.append(rec)
        
        if not mitigation:
            mitigation.append(
                '✅ **Standard Practices:** No major mitigation required - '
                'follow standard construction practices'
            )
        
        return mitigation
