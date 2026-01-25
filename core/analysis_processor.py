# ============================================================================
# FILE: core/analysis_processor.py (ADD EE CHECK)
# ============================================================================

from typing import Dict
from utils.ee_manager import EarthEngineManager
from utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisProcessor:
    """Coordinate the overall analysis workflow"""
    
    def __init__(self):
        self.ee_available = EarthEngineManager.is_available()
        
        # Only import EE-dependent modules if available
        if self.ee_available:
            from data.earth_engine.gee_client import GEEClient
            from data.feature_extraction.terrain_features import TerrainFeatureExtractor
            from data.feature_extraction.environmental_features import EnvironmentalFeatureExtractor
            
            self.gee_client = GEEClient()
            self.terrain_extractor = TerrainFeatureExtractor()
            self.env_extractor = EnvironmentalFeatureExtractor()
        
        # These don't require EE
        from data.feature_extraction.infrastructure_features import InfrastructureFeatureExtractor
        from intelligence.ahp.ahp_solver import AHPSolver
        from intelligence.ml.models.suitability_predictor import SuitabilityPredictor
        from intelligence.recommendation.score_aggregator import ScoreAggregator
        
        self.infra_extractor = InfrastructureFeatureExtractor()
        self.ahp_solver = AHPSolver()
        self.ml_predictor = SuitabilityPredictor()
        self.score_aggregator = ScoreAggregator()
    
    def run_analysis(
        self,
        boundary_data: Dict,
        criteria: Dict,
        progress_callback=None
    ) -> Dict:
        """Run complete land evaluation analysis"""
        
        # Check if EE is required
        if not self.ee_available:
            raise RuntimeError(
                "Google Earth Engine is required for analysis. "
                "Please authenticate: earthengine authenticate"
            )
        
        try:
            logger.info("Starting land evaluation analysis")
            
            # Continue with normal analysis...
            if progress_callback:
                progress_callback("Collecting satellite and terrain data...", 10)
            
            features = self._extract_all_features(boundary_data)
            
            # ... rest of the analysis code ...
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise