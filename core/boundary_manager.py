# ============================================================================
# FILE: core/boundary_manager.py
# Converts raw coordinates / GeoJSON into the standard boundary_data dict
# ============================================================================

from shapely.geometry import Polygon, mapping, shape
from typing import Dict, List, Optional
import logging

from utils.geometry_utils import GeometryUtils

logger = logging.getLogger(__name__)


class BoundaryManager:
    """
    Single source of truth for boundary creation.

    Every other module (analysis pipeline, heatmap, risk engine) receives
    boundary data as a plain dict with these guaranteed keys:

        geometry        – Shapely Polygon
        centroid        – [lon, lat]
        area_m2         – float
        area_hectares   – float
        area_acres      – float
        perimeter_m     – float
        geojson         – GeoJSON Feature dict  (for Folium rendering)
        ee_geometry     – ee.Geometry or None   (when Earth Engine is live)
        coordinates     – list of [lon, lat] pairs (the raw input ring)
    """

    # 1 hectare = 10 000 m²;  1 acre ≈ 4 046.86 m²
    _M2_PER_HECTARE = 10_000.0
    _M2_PER_ACRE   = 4_046.8564224

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def create_from_coordinates(self, coords: List[List[float]]) -> Dict:
        """
        Build boundary_data from a list of [lon, lat] coordinate pairs.

        Args:
            coords: e.g. [[5.41, 36.19], [5.42, 36.19], …]
                    The ring does NOT need to be explicitly closed; this method
                    closes it automatically if the first and last points differ.

        Returns:
            boundary_data dict (see class docstring).

        Raises:
            ValueError: if fewer than 3 unique points or the polygon is invalid.
        """
        coords = self._close_ring(coords)

        if len(coords) < 4:          # need ≥ 3 unique + closing duplicate
            raise ValueError(
                f"Need at least 3 points to form a polygon, got {len(coords) - 1}"
            )

        polygon = Polygon(coords)

        if not polygon.is_valid:
            # buffer(0) fixes most simple self-intersection issues
            polygon = polygon.buffer(0)
            if not polygon.is_valid:
                raise ValueError(
                    "Polygon geometry is invalid and could not be auto-repaired"
                )

        return self._build_boundary_data(polygon, coords)

    def import_from_geojson_dict(self, geojson: Dict) -> Dict:
        """
        Build boundary_data from a parsed GeoJSON dict.

        Accepts a GeoJSON Feature, FeatureCollection (uses first feature),
        or bare Geometry object.

        Raises:
            ValueError: if no usable polygon geometry is found.
        """
        geometry_dict = self._extract_geometry(geojson)

        if geometry_dict is None:
            raise ValueError("No polygon geometry found in the provided GeoJSON")

        polygon = shape(geometry_dict)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)
            if not polygon.is_valid:
                raise ValueError(
                    "GeoJSON polygon is invalid and could not be auto-repaired"
                )

        coords = list(polygon.exterior.coords)
        return self._build_boundary_data(polygon, coords)

    # ---------------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------------

    def _build_boundary_data(self, polygon: Polygon, coords: List) -> Dict:
        """Core logic shared by both public entry-points."""

        area_m2     = GeometryUtils.calculate_area(polygon)
        perimeter_m = GeometryUtils.calculate_perimeter(polygon)
        centroid    = GeometryUtils.get_centroid(polygon)   # (lon, lat)

        geojson_feature = {
            "type": "Feature",
            "properties": {},
            "geometry": mapping(polygon)
        }

        boundary_data = {
            "geometry":      polygon,
            "centroid":      list(centroid),                # [lon, lat]
            "area_m2":       area_m2,
            "area_hectares": area_m2 / self._M2_PER_HECTARE,
            "area_acres":    area_m2 / self._M2_PER_ACRE,
            "perimeter_m":   perimeter_m,
            "geojson":       geojson_feature,
            "coordinates":   coords,
            "ee_geometry":   self._try_create_ee_geometry(coords),
        }

        logger.info(
            f"Boundary created: {boundary_data['area_hectares']:.2f} ha, "
            f"centroid={centroid}"
        )

        return boundary_data

    @staticmethod
    def _close_ring(coords: List[List[float]]) -> List[List[float]]:
        """Ensure the coordinate ring is closed (first == last)."""
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]
        return coords

    @staticmethod
    def _extract_geometry(geojson: Dict) -> Optional[Dict]:
        """
        Pull a Polygon/MultiPolygon geometry dict out of various GeoJSON shapes.
        Returns None if nothing usable is found.
        """
        geo_type = geojson.get("type", "")

        if geo_type in ("Polygon", "MultiPolygon"):
            return geojson

        if geo_type == "Feature":
            return geojson.get("geometry")

        if geo_type == "FeatureCollection":
            for feature in geojson.get("features", []):
                geom = feature.get("geometry", {})
                if geom.get("type") in ("Polygon", "MultiPolygon"):
                    return geom

        return None

    @staticmethod
    def _try_create_ee_geometry(coords: List) -> Optional[object]:
        """
        Attempt to create an ee.Geometry.Polygon.
        Returns None quietly if Earth Engine is not initialised.
        """
        try:
            from utils.ee_manager import EarthEngineManager
            if EarthEngineManager.is_available():
                import ee
                return ee.Geometry.Polygon([coords])
        except Exception as e:
            logger.debug(f"ee.Geometry creation skipped: {e}")

        return None
