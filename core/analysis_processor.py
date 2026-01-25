# ============================================================================
# FILE: core/analysis_processor.py
# Fully corrected AnalysisProcessor
# ============================================================================

from typing import Dict, Optional, Callable
from utils.ee_manager import EarthEngineManager
from utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisProcessor:
    """Coordinate the complete land evaluation workflow."""

    def __init__(self):
        # Check if EE is available
        self.ee_available = EarthEngineManager.is_available()

        # EE-dependent modules
        if self.ee_available:
            from data.earth_engine.gee_client import GEEClient
            from data.feature_extraction.terrain_features import TerrainFeatureExtractor
            from data.feature_extraction.environmental_features import EnvironmentalFeatureExtractor

            self.gee_client = GEEClient()
            self.terrain_extractor = TerrainFeatureExtractor()
            self.env_extractor = EnvironmentalFeatureExtractor()
        else:
            self.gee_client = None
            self.terrain_extractor = None
            self.env_extractor = None

        # EE-independent modules
        from data.feature_extraction.infrastructure_features import InfrastructureFeatureExtractor
        from intelligence.ahp.ahp_solver import AHPSolver
        from intelligence.ml.models.suitability_predictor import SuitabilityPredictor
        from intelligence.recommendation.score_aggregator import ScoreAggregator

        self.infra_extractor = InfrastructureFeatureExtractor()
        self.ahp_solver = AHPSolver()
        self.ml_predictor = SuitabilityPredictor()
        self.score_aggregator = ScoreAggregator()

    # -----------------------------
    # Public method to run analysis
    # -----------------------------
    def run_analysis(
        self,
        boundary_data: Dict,
        criteria: Dict,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict:
        """Run the full land evaluation analysis pipeline."""
        
        if not self.ee_available:
            raise RuntimeError(
                "Google Earth Engine is required for analysis. "
                "Please authenticate: earthengine authenticate"
            )

        logger.info("Starting land evaluation analysis...")
        results = {}

        try:
            # -----------------------------
            # Step 1: Extract features
            # -----------------------------
            if progress_callback:
                progress_callback("Collecting satellite and terrain data...", 10)

            # Terrain features
            terrain_features = self.terrain_extractor.extract(boundary_data)
            results['terrain_features'] = terrain_features

            # Environmental features
            env_features = self.env_extractor.extract(boundary_data)
            results['environmental_features'] = env_features

            # Infrastructure features (requires geometry)
            infra_features = self.infra_extractor.extract(boundary_data['geometry'])
            results['infrastructure_features'] = infra_features

            if progress_callback:
                progress_callback("Features extracted successfully", 40)

            # -----------------------------
            # Step 2: AHP weighting
            # -----------------------------
            if progress_callback:
                progress_callback("Computing AHP weights...", 50)

            weights = self.ahp_solver.compute_weights(criteria)
            results['weights'] = weights

            # -----------------------------
            # Step 3: Machine learning suitability prediction
            # -----------------------------
            if progress_callback:
                progress_callback("Predicting land suitability...", 70)

            suitability_map = self.ml_predictor.predict(results)
            results['suitability_map'] = suitability_map

            # -----------------------------
            # Step 4: Aggregate scores & recommendations
            # -----------------------------
            if progress_callback:
                progress_callback("Aggregating scores and generating recommendations...", 90)

            recommendations = self.score_aggregator.aggregate(results)
            results['recommendations'] = recommendations

            if progress_callback:
                progress_callback("Analysis complete!", 100)

            logger.info("Land evaluation analysis completed successfully.")
            return results

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
