# ============================================================================
# FILE: core/analysis_processor.py (with _extract_all_features implemented)
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

    def _extract_all_features(self, boundary_data: Dict) -> Dict:
        """
        Extract all features for the analysis:
        - Terrain (DEM, slope, aspect)
        - Environmental (NDVI, water, landcover)
        - Infrastructure (roads, services)
        """

        logger.info("Extracting all features...")

        all_features = {}

        # Terrain features (EE required)
        if self.ee_available:
            terrain_features = self.terrain_extractor.extract(boundary_data)
            env_features = self.env_extractor.extract(boundary_data)
            all_features.update(terrain_features)
            all_features.update(env_features)
        else:
            logger.warning("EE not available, skipping terrain/environmental features")

        # Infrastructure features (local)
        infra_features = self.infra_extractor.extract(boundary_data)
        all_features.update(infra_features)

        logger.info("Feature extraction complete")
        return all_features

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

            if progress_callback:
                progress_callback("Collecting satellite and terrain data...", 10)

            # Extract all features
            features = self._extract_all_features(boundary_data)

            if progress_callback:
                progress_callback("Calculating scores and suitability...", 50)

            # Example: calculate AHP weights and ML prediction
            ahp_scores = self.ahp_solver.compute(criteria, features)
            ml_scores = self.ml_predictor.predict(features)
            suitability_scores = self.score_aggregator.aggregate(ahp_scores, ml_scores)

            if progress_callback:
                progress_callback("Analysis complete!", 100)

            logger.info("Land evaluation analysis complete")
            return {
                "features": features,
                "ahp_scores": ahp_scores,
                "ml_scores": ml_scores,
                "suitability_scores": suitability_scores
            }

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
