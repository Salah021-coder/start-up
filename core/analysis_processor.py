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
        # Step 1: Extract terrain features
        if self.terrain_extractor:
            if progress_callback:
                progress_callback("Collecting terrain features...", 10)
            results['terrain_features'] = self.terrain_extractor.extract(boundary_data)

        # Step 2: Extract environmental features
        if self.env_extractor:
            if progress_callback:
                progress_callback("Collecting environmental features...", 20)
            results['environmental_features'] = self.env_extractor.extract(boundary_data)

        # Step 3: Extract infrastructure features (requires geometry)
        if progress_callback:
            progress_callback("Collecting infrastructure features...", 30)

        # Safe geometry extraction
        geometry = None
        if 'geometry' in boundary_data:
            geometry = boundary_data['geometry']
        elif 'geojson' in boundary_data:
            geometry = boundary_data['geojson']
        else:
            # fallback: maybe the boundary_data itself is geometry
            geometry = boundary_data

        results['infrastructure_features'] = self.infra_extractor.extract(geometry)

        if progress_callback:
            progress_callback("Features extracted successfully", 50)

        # Step 4: Compute AHP weights
        if progress_callback:
            progress_callback("Computing AHP weights...", 60)
        results['weights'] = self.ahp_solver.compute_weights(criteria)

        # Step 5: ML suitability prediction
        if progress_callback:
            progress_callback("Predicting land suitability...", 80)
        results['suitability_map'] = self.ml_predictor.predict(results)

        # Step 6: Aggregate scores & recommendations
        if progress_callback:
            progress_callback("Aggregating scores and generating recommendations...", 90)
        results['recommendations'] = self.score_aggregator.aggregate(results)

        if progress_callback:
            progress_callback("Analysis complete!", 100)

        logger.info("Land evaluation analysis completed successfully.")
        return results

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise
