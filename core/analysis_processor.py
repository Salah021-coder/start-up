# ============================================================================
# FILE: core/analysis_processor.py
# Orchestrates a full land analysis and returns a plain dict for the UI
# ============================================================================

from typing import Dict, Optional, Callable
import logging

from services.analysis_service import get_analysis_service
from core.orchestration.analysis_pipeline import PipelineConfig

logger = logging.getLogger(__name__)


class AnalysisProcessor:
    """
    Thin orchestration layer called by  ui/pages/analysis.py.

    Responsibilities:
        1. Receives boundary_data (dict) and criteria (dict) from the UI.
        2. Delegates the heavy lifting to AnalysisService → AnalysisPipeline.
        3. Converts the returned AnalysisResult dataclass into a plain dict
           so that results.py, risk_analysis.py, the chatbot, etc. can all
           safely call  results.get('key')  without crashing.
        4. Surfaces errors as plain strings the UI can display.
    """

    def __init__(self):
        self._config = PipelineConfig(
            use_real_osm=True,
            enable_ml_predictions=False,
            include_recommendations=True,
            recommendation_count=10,
        )

    def run_analysis(
        self,
        boundary_data: Dict,
        criteria: Dict,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Dict:
        """
        Execute the full analysis pipeline.

        Args:
            boundary_data: Standard boundary dict from BoundaryManager.
            criteria:      Nested weight dict (the value under the 'criteria'
                           key returned by CriteriaEngine).  Stored for potential
                           future use; the pipeline currently auto-selects its
                           own criteria internally via AHPEngine.
            progress_callback: Optional  callback(message, percent)  forwarded
                               to the pipeline for the UI progress bar.

        Returns:
            A plain ``dict`` that every UI page can safely call ``.get()`` on.
            Shape matches AnalysisResult.to_legacy_format().

        Raises:
            RuntimeError: with a user-friendly message if anything goes wrong.
        """
        # --- guard: types ----------------------------------------------------------
        if not isinstance(boundary_data, dict):
            raise RuntimeError(
                f"❌ Internal error: boundary_data is {type(boundary_data).__name__}, "
                "expected dict. Check BoundaryManager output."
            )

        if not isinstance(criteria, dict):
            raise RuntimeError(
                f"❌ Internal error: criteria is {type(criteria).__name__}, "
                "expected dict. Check CriteriaEngine output."
            )

        logger.info("AnalysisProcessor.run_analysis started")

        # --- delegate to the service layer -----------------------------------------
        service = get_analysis_service(self._config)

        result, error_msg = service.analyze_land(
            boundary_data=boundary_data,
            progress_callback=progress_callback,
        )

        if error_msg:
            # AnalysisService already formatted this for the user
            raise RuntimeError(error_msg)

        # --- convert AnalysisResult dataclass → plain dict -------------------------
        # The UI pages all do  results.get('features', {})  etc., which only works
        # on dicts.  to_legacy_format() produces exactly the shape they expect.
        try:
            results_dict = result.to_legacy_format()
        except AttributeError:
            # Safety net: if result is somehow already a dict, use it directly.
            if isinstance(result, dict):
                results_dict = result
            else:
                raise RuntimeError(
                    "❌ Analysis returned an unexpected result type: "
                    f"{type(result).__name__}. Cannot convert to display format."
                )

        logger.info(
            f"AnalysisProcessor complete — "
            f"score={results_dict.get('overall_score', '?')}/10"
        )

        return results_dict
