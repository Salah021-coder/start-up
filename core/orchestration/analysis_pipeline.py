# ============================================================================
# FILE: core/orchestration/analysis_pipeline.py
# Main Analysis Pipeline Orchestrator
# ============================================================================

from typing import Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid

from core.models.analysis_result import AnalysisResult, AnalysisMetadata
from core.features.terrain import TerrainExtractor
from core.features.environmental import EnvironmentalExtractor
from core.features.infrastructure import InfrastructureExtractor
from core.risk import RiskEngine
from core.risk.signal_adapter import FeatureToSignalAdapter
from core.suitability.ahp_engine import AHPEngine
from core.recommendation.usage_recommender import UsageRecommender

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for analysis pipeline"""
    use_real_osm: bool = True
    enable_ml_predictions: bool = False
    max_area_km2: float = 100.0
    include_recommendations: bool = True
    recommendation_count: int = 10


class AnalysisPipeline:
    """
    Orchestrates the complete land analysis workflow
    
    RESPONSIBILITIES:
    1. Coordinates all feature extraction
    2. Manages data flow between stages
    3. Handles errors gracefully
    4. Logs everything
    5. Returns immutable AnalysisResult
    
    DOES NOT:
    - Compute anything itself (delegates)
    - Make UI decisions
    - Store session state
    - Use fallbacks silently
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize pipeline with all required components
        
        Args:
            config: Pipeline configuration (uses defaults if None)
        """
        self.config = config or PipelineConfig()
        
        # Initialize extractors
        self._init_extractors()
        
        # Initialize engines
        self._init_engines()
        
        logger.info(
            f"Analysis pipeline initialized with config: "
            f"OSM={self.config.use_real_osm}, "
            f"ML={self.config.enable_ml_predictions}"
        )
    
    def _init_extractors(self):
        """Initialize all feature extractors"""
        
        # Check EE availability
        self.ee_available = self._check_ee_available()
        
        if self.ee_available:
            logger.info("Earth Engine available - will use real GEE data")
            self.terrain_extractor = TerrainExtractor()
            self.env_extractor = EnvironmentalExtractor()
        else:
            logger.warning("Earth Engine NOT available - limited functionality")
            self.terrain_extractor = None
            self.env_extractor = None
        
        # Infrastructure always available
        self.infra_extractor = InfrastructureExtractor(
            use_real_osm=self.config.use_real_osm
        )
    
    def _init_engines(self):
        """Initialize analysis engines"""
        
        # Risk engine (always available)
        ml_adapter = None
        if self.config.enable_ml_predictions:
            try:
                from core.risk.ml_adapter import RiskMLAdapter
                ml_adapter = RiskMLAdapter()
                logger.info("ML adapter loaded for risk assessment")
            except ImportError:
                logger.warning("ML adapter not available - using rules only")
        
        self.risk_engine = RiskEngine(ml_adapter=ml_adapter)
        self.signal_adapter = FeatureToSignalAdapter()
        
        # Suitability engine
        self.ahp_engine = AHPEngine()
        
        # Recommendation engine
        self.recommender = UsageRecommender()
    
    def _check_ee_available(self) -> bool:
        """Check if Earth Engine is available"""
        try:
            import ee
            ee.String('test').getInfo()
            return True
        except:
            return False
    
    def run_analysis(
        self,
        boundary_data: Dict,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> AnalysisResult:
        """
        Run complete land analysis pipeline
        
        Args:
            boundary_data: Boundary geometry and metadata
            progress_callback: Optional callback(message, percent)
            
        Returns:
            Immutable AnalysisResult
            
        Raises:
            ValueError: If boundary invalid or insufficient data
            RuntimeError: If critical stage fails
        """
        # Generate unique analysis ID
        analysis_id = self._generate_analysis_id()
        
        logger.info(f"Starting analysis {analysis_id}")
        start_time = datetime.now()
        
        try:
            # Stage 1: Validate boundary
            self._update_progress(progress_callback, "Validating boundary...", 5)
            self._validate_boundary(boundary_data)
            
            # Stage 2: Extract features
            self._update_progress(progress_callback, "Extracting features...", 10)
            features = self._extract_features(boundary_data, progress_callback)
            
            # Stage 3: Assess risks
            self._update_progress(progress_callback, "Assessing risks...", 50)
            risk_result = self._assess_risks(features)
            
            # Stage 4: Calculate suitability
            self._update_progress(progress_callback, "Calculating suitability...", 70)
            suitability_result = self._calculate_suitability(features, risk_result)
            
            # Stage 5: Generate recommendations
            if self.config.include_recommendations:
                self._update_progress(progress_callback, "Generating recommendations...", 85)
                recommendations = self._generate_recommendations(
                    features, 
                    risk_result,
                    suitability_result
                )
            else:
                recommendations = []
            
            # Stage 6: Compile final result
            self._update_progress(progress_callback, "Finalizing results...", 95)
            result = self._compile_result(
                analysis_id=analysis_id,
                boundary_data=boundary_data,
                features=features,
                risk_result=risk_result,
                suitability_result=suitability_result,
                recommendations=recommendations,
                start_time=start_time
            )
            
            self._update_progress(progress_callback, "Analysis complete!", 100)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Analysis {analysis_id} completed in {duration:.2f}s, "
                f"score={result.overall_score:.1f}/10"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}", exc_info=True)
            raise
    
    def _validate_boundary(self, boundary_data: Dict):
        """Validate boundary meets requirements"""
        
        if not boundary_data:
            raise ValueError("Boundary data is empty")
        
        if 'geometry' not in boundary_data:
            raise ValueError("Boundary missing geometry")
        
        area_m2 = boundary_data.get('area_m2', 0)
        area_km2 = area_m2 / 1_000_000
        
        if area_km2 > self.config.max_area_km2:
            raise ValueError(
                f"Area too large: {area_km2:.2f} km² "
                f"(max: {self.config.max_area_km2} km²)"
            )
        
        if area_m2 < 100:
            raise ValueError(f"Area too small: {area_m2:.0f} m² (min: 100 m²)")
        
        logger.info(f"Boundary validated: {area_km2:.2f} km²")
    
    def _extract_features(
        self,
        boundary_data: Dict,
        progress_callback: Optional[Callable]
    ) -> Dict:
        """
        Extract all features from boundary
        
        Returns:
            Dict with keys: terrain, environmental, infrastructure, boundary
        """
        features = {}
        
        ee_geometry = boundary_data.get('ee_geometry')
        shapely_geometry = boundary_data.get('geometry')
        centroid = boundary_data.get('centroid')
        
        # Extract terrain (requires EE)
        self._update_progress(progress_callback, "Extracting terrain features...", 15)
        
        if self.ee_available and ee_geometry and self.terrain_extractor:
            try:
                features['terrain'] = self.terrain_extractor.extract(ee_geometry)
                logger.info("Terrain features extracted from Earth Engine")
            except Exception as e:
                logger.error(f"Terrain extraction failed: {e}")
                raise RuntimeError(f"Cannot proceed without terrain data: {e}")
        else:
            logger.error("Earth Engine not available - cannot extract terrain")
            raise RuntimeError(
                "Earth Engine required for terrain analysis. "
                "Please configure GEE credentials."
            )
        
        # Extract environmental (requires EE)
        self._update_progress(progress_callback, "Extracting environmental features...", 30)
        
        if self.ee_available and ee_geometry and self.env_extractor:
            try:
                features['environmental'] = self.env_extractor.extract(
                    ee_geometry,
                    terrain_features=features['terrain']
                )
                logger.info("Environmental features extracted")
            except Exception as e:
                logger.warning(f"Environmental extraction failed: {e}")
                # Environmental is less critical - can continue
                features['environmental'] = self._get_minimal_environmental()
        else:
            features['environmental'] = self._get_minimal_environmental()
        
        # Extract infrastructure (always available)
        self._update_progress(progress_callback, "Extracting infrastructure features...", 40)
        
        try:
            features['infrastructure'] = self.infra_extractor.extract(
                ee_geometry=ee_geometry,
                centroid=centroid,
                geometry=shapely_geometry
            )
            logger.info(
                f"Infrastructure features extracted "
                f"(quality: {features['infrastructure'].get('data_quality')})"
            )
        except Exception as e:
            logger.error(f"Infrastructure extraction failed: {e}")
            raise RuntimeError(f"Infrastructure extraction failed: {e}")
        
        features['boundary'] = boundary_data
        
        return features
    
    def _assess_risks(self, features: Dict):
        """
        Assess all risks using centralized engine
        
        Returns:
            ComprehensiveRiskResult
            
        Raises:
            ValueError: If insufficient data for risk assessment
        """
        try:
            # Convert features to signals
            signals = self.signal_adapter.convert_all_features(features)
            location = self.signal_adapter.extract_location(features)
            
            logger.info(f"Converted {len(signals)} signals for risk assessment")
            
            # Run risk assessment
            risk_result = self.risk_engine.assess_all_risks(
                signals=signals,
                location=location
            )
            
            logger.info(
                f"Risk assessment complete: {risk_result.overall_level.name}, "
                f"avg severity {risk_result.average_severity:.1f}/5"
            )
            
            return risk_result
            
        except ValueError as e:
            logger.error(f"Risk assessment validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}", exc_info=True)
            raise RuntimeError(f"Risk assessment failed: {e}")
    
    def _calculate_suitability(self, features: Dict, risk_result) -> Dict:
        """
        Calculate suitability using AHP
        
        Returns:
            Dict with AHP scores and weights
        """
        try:
            # Auto-select criteria based on features
            criteria = self.ahp_engine.auto_select_criteria(
                features=features,
                risk_result=risk_result
            )
            
            # Calculate suitability scores
            suitability = self.ahp_engine.calculate_suitability(
                features=features,
                criteria=criteria
            )
            
            logger.info(
                f"Suitability calculated: overall {suitability['overall_score']:.1f}/10"
            )
            
            return suitability
            
        except Exception as e:
            logger.error(f"Suitability calculation failed: {e}", exc_info=True)
            raise RuntimeError(f"Suitability calculation failed: {e}")
    
    def _generate_recommendations(
        self,
        features: Dict,
        risk_result,
        suitability_result: Dict
    ) -> list:
        """
        Generate land use recommendations
        
        Returns:
            List of recommendations sorted by suitability
        """
        try:
            recommendations = self.recommender.generate_recommendations(
                features=features,
                risk_result=risk_result,
                suitability_scores=suitability_result,
                top_n=self.config.recommendation_count
            )
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}", exc_info=True)
            # Recommendations are optional - can continue without
            return []
    
    def _compile_result(
        self,
        analysis_id: str,
        boundary_data: Dict,
        features: Dict,
        risk_result,
        suitability_result: Dict,
        recommendations: list,
        start_time: datetime
    ) -> AnalysisResult:
        """
        Compile all results into immutable AnalysisResult
        
        This is the ONLY place where AnalysisResult is created
        """
        # Calculate overall metrics
        overall_score = suitability_result.get('overall_score', 0)
        confidence = self._calculate_confidence(features, risk_result)
        
        # Create metadata
        metadata = AnalysisMetadata(
            analysis_id=analysis_id,
            timestamp=start_time.isoformat(),
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            pipeline_version="2.0",
            ee_available=self.ee_available,
            osm_quality=features['infrastructure'].get('data_quality', 'unknown'),
            ml_enabled=self.config.enable_ml_predictions
        )
        
        # Create immutable result
        result = AnalysisResult(
            metadata=metadata,
            boundary=boundary_data,
            features=features,
            risk_assessment=risk_result,
            suitability=suitability_result,
            recommendations=recommendations,
            overall_score=overall_score,
            confidence_level=confidence
        )
        
        return result
    
    def _calculate_confidence(self, features: Dict, risk_result) -> float:
        """Calculate overall confidence in results"""
        
        confidence_factors = []
        
        # Data quality
        terrain_quality = features.get('terrain', {}).get('data_quality', 'unknown')
        if terrain_quality == 'gee':
            confidence_factors.append(0.95)
        else:
            confidence_factors.append(0.60)
        
        # Infrastructure quality
        infra_quality = features['infrastructure'].get('data_quality', 'unknown')
        if infra_quality == 'real_osm':
            confidence_factors.append(0.90)
        elif infra_quality == 'enhanced':
            confidence_factors.append(0.75)
        else:
            confidence_factors.append(0.60)
        
        # Risk assessment confidence
        # Average confidence from all risk assessments
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
    
    def _get_minimal_environmental(self) -> Dict:
        """Minimal environmental data when extraction fails"""
        logger.warning("Using minimal environmental data")
        return {
            'ndvi_avg': 0.5,
            'ndvi_min': 0.2,
            'ndvi_max': 0.8,
            'land_cover_distribution': {},
            'dominant_cover': 'unknown',
            'water_occurrence_avg': 0.0,
            'water_occurrence_max': 0.0,
            'air_quality_estimate': 'unknown',
            'data_quality': 'minimal'
        }
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
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


# ============================================================================
# Pipeline Context Manager (for batch processing)
# ============================================================================

class PipelineContext:
    """
    Context manager for running multiple analyses
    
    Usage:
        with PipelineContext(config) as pipeline:
            result1 = pipeline.run_analysis(boundary1)
            result2 = pipeline.run_analysis(boundary2)
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config
        self.pipeline = None
    
    def __enter__(self):
        """Initialize pipeline on context entry"""
        self.pipeline = AnalysisPipeline(self.config)
        logger.info("Pipeline context opened")
        return self.pipeline
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit"""
        if exc_type:
            logger.error(
                f"Pipeline context closed with error: {exc_type.__name__}: {exc_val}"
            )
        else:
            logger.info("Pipeline context closed successfully")
        
        # Cleanup if needed
        self.pipeline = None
        
        # Don't suppress exceptions
        return False
