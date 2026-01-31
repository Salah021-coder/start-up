# ============================================================================
# FILE: core/criteria_engine.py
# Selects and returns evaluation criteria for a given boundary
# ============================================================================

from typing import Dict
import logging

from config.criteria_config import CriteriaConfig

logger = logging.getLogger(__name__)


class CriteriaEngine:
    """
    Decides which evaluation criteria (and weights) to apply.

    Thin facade over CriteriaConfig so that analysis.py can call a single
    method and get back a ready-to-use dict.

    Return shape (analysis.py uses  criteria['criteria'] ):
        {
            "criteria":  { <nested category → criterion → weight> },
            "land_use":  "residential" | "commercial" | …
        }
    """

    def auto_select_criteria(self, boundary_data: Dict) -> Dict:
        """
        Automatically pick criteria weights based on location characteristics.

        Args:
            boundary_data: The standard boundary_data dict produced by
                           BoundaryManager.

        Returns:
            Dict with keys 'criteria' and 'land_use'.

        Raises:
            TypeError: if boundary_data is not a dict (early signal that
                       BoundaryManager returned something unexpected).
        """
        if not isinstance(boundary_data, dict):
            raise TypeError(
                f"boundary_data must be a dict, got {type(boundary_data).__name__}. "
                "Check BoundaryManager output."
            )

        # Pull whatever location hints exist in the boundary dict.
        # These are the same keys CriteriaConfig.auto_select_criteria expects.
        location_data = {
            "urbanization_level":    boundary_data.get("urbanization_level",    "suburban"),
            "population_density":    boundary_data.get("population_density",    500),
            "nearest_road_distance": boundary_data.get("nearest_road_distance", 1000),
            "electricity_grid":      boundary_data.get("electricity_grid",      True),
            "water_network":         boundary_data.get("water_network",         True),
            "sewage_system":         boundary_data.get("sewage_system",         True),
        }

        land_use         = self._infer_land_use(location_data)
        criteria_weights = CriteriaConfig.get_criteria_for_use(land_use)
        criteria_weights = CriteriaConfig._normalize_weights(criteria_weights)

        logger.info(f"Selected criteria for land_use='{land_use}'")

        return {
            "criteria": criteria_weights,
            "land_use": land_use,
        }

    def get_criteria_for_use(self, land_use: str) -> Dict:
        """
        Explicit criteria lookup by land-use type.
        Returns the same shape as auto_select_criteria.
        """
        criteria_weights = CriteriaConfig.get_criteria_for_use(land_use)
        criteria_weights = CriteriaConfig._normalize_weights(criteria_weights)

        return {
            "criteria": criteria_weights,
            "land_use": land_use,
        }

    # ---------------------------------------------------------------------------
    # Internal
    # ---------------------------------------------------------------------------

    @staticmethod
    def _infer_land_use(location_data: Dict) -> str:
        """Simple heuristic to pick a default land-use from location hints."""
        urban = location_data.get("urbanization_level", "suburban")
        pop   = location_data.get("population_density", 500)

        if urban in ("city_center", "urban") or pop > 2000:
            return "commercial"
        elif urban == "rural" or pop < 100:
            return "agricultural"
        else:
            return "residential"
