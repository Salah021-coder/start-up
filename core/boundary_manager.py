# ============================================================================
# FILE: core/boundary_manager.py
# Manages land boundary creation, validation, and format conversion
# ============================================================================

from shapely.geometry import Polygon, mapping, shape
from typing import Dict, List, Optional, Tuple
import json
import logging
import math

from utils.geometry_utils import GeometryUtils

logger = logging.getLogger(__name__)


class BoundaryManager:
    """
    Manages all boundary operations:
    - Create from coordinate lists
    - Import from GeoJSON / KML
    - Validate geometry
    - Compute area, perimeter, centroid
    - Export to EE geometry (if available)
    """

    MAX_AREA_KM2 = 100.0   # 100 km² hard cap
    MIN_AREA_M2 = 100.0    # 100 m² minimum
    MAX_VERTICES = 10000

    def __init__(self):
        self._ee_available = self._check_ee()

    # ------------------------------------------------------------------
    # PUBLIC CREATION METHODS
    # ------------------------------------------------------------------

    def create_from_coordinates(self, coords: List[List[float]]) -> Dict:
        """
        Create boundary from a list of [lon, lat] pairs.

        Args:
            coords: List of [longitude, latitude] coordinate pairs.
                    First and last point should be identical (closed ring).

        Returns:
            Boundary dict with geometry, area, perimeter, centroid, geojson, etc.

        Raises:
            ValueError: Invalid or too-small / too-large geometry.
        """
        if not coords or len(coords) < 4:
            raise ValueError("At least 4 coordinate pairs required (closed polygon).")

        # Ensure ring is closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        # Validate coordinates
        self._validate_coordinate_list(coords)

        # Build Shapely polygon
        polygon = Polygon(coords)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)  # auto-fix minor topology issues
            if not polygon.is_valid:
                raise ValueError("Could not create a valid polygon from these coordinates.")

        return self._build_boundary_dict(polygon, coords)

    def import_from_geojson_dict(self, geojson: Dict) -> Dict:
        """
        Import boundary from a parsed GeoJSON dict (Feature or FeatureCollection).

        Returns:
            Boundary dict (same structure as create_from_coordinates).
        """
        feature = self._extract_feature(geojson)
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type", "")

        if geom_type == "Polygon":
            ring = geometry["coordinates"][0]
        elif geom_type == "MultiPolygon":
            # Take the largest polygon
            ring = max(geometry["coordinates"], key=lambda p: Polygon(p[0]).area)[0]
        else:
            raise ValueError(f"Unsupported GeoJSON geometry type: {geom_type}")

        polygon = shape(geometry) if geom_type == "Polygon" else Polygon(ring)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        return self._build_boundary_dict(polygon, list(ring))

    def import_from_kml_string(self, kml_string: str) -> Dict:
        """
        Import boundary from a KML string.
        Parses the first <coordinates> block found.
        """
        import re

        match = re.search(
            r"<coordinates>\s*(.*?)\s*</coordinates>", kml_string, re.DOTALL
        )
        if not match:
            raise ValueError("No <coordinates> element found in KML.")

        raw = match.group(1).strip()
        # KML coordinates: "lon,lat,alt lon,lat,alt ..."
        coords = []
        for triplet in raw.split():
            parts = triplet.split(",")
            if len(parts) >= 2:
                coords.append([float(parts[0]), float(parts[1])])

        return self.create_from_coordinates(coords)

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def validate_boundary(self, boundary_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate an existing boundary dict.

        Returns:
            (is_valid, list_of_error_messages)
        """
        errors = []
        geometry = boundary_data.get("geometry")

        if geometry is None:
            errors.append("Missing 'geometry' field.")
            return False, errors

        if not geometry.is_valid:
            errors.append("Polygon geometry is not valid.")

        area_m2 = boundary_data.get("area_m2", 0)
        if area_m2 < self.MIN_AREA_M2:
            errors.append(f"Area too small: {area_m2:.0f} m² (min {self.MIN_AREA_M2:.0f} m²).")

        area_km2 = area_m2 / 1_000_000
        if area_km2 > self.MAX_AREA_KM2:
            errors.append(f"Area too large: {area_km2:.2f} km² (max {self.MAX_AREA_KM2} km²).")

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------

    def _build_boundary_dict(self, polygon: Polygon, raw_coords: List) -> Dict:
        """Compute all derived metrics and return the full boundary dict."""
        area_m2 = GeometryUtils.calculate_area(polygon)
        area_km2 = area_m2 / 1_000_000
        area_hectares = area_m2 / 10_000
        area_acres = area_hectares * 2.47105

        if area_m2 < self.MIN_AREA_M2:
            raise ValueError(f"Area too small: {area_m2:.0f} m² (minimum {self.MIN_AREA_M2:.0f} m²).")
        if area_km2 > self.MAX_AREA_KM2:
            raise ValueError(f"Area too large: {area_km2:.2f} km² (maximum {self.MAX_AREA_KM2} km²).")

        perimeter_m = GeometryUtils.calculate_perimeter(polygon)
        centroid = GeometryUtils.get_centroid(polygon)  # (lon, lat)

        geojson_feature = {
            "type": "Feature",
            "geometry": mapping(polygon),
            "properties": {
                "area_m2": area_m2,
                "area_hectares": area_hectares,
                "perimeter_m": perimeter_m,
            },
        }

        boundary = {
            "geometry": polygon,
            "coordinates": raw_coords,
            "area_m2": area_m2,
            "area_km2": area_km2,
            "area_hectares": round(area_hectares, 4),
            "area_acres": round(area_acres, 4),
            "perimeter_m": round(perimeter_m, 2),
            "centroid": list(centroid),  # [lon, lat]
            "geojson": geojson_feature,
            "bounds": list(polygon.bounds),  # (minx, miny, maxx, maxy)
        }

        # Attach EE geometry if available
        if self._ee_available:
            try:
                import ee
                ee_coords = [[lon, lat] for lon, lat in raw_coords]
                boundary["ee_geometry"] = ee.Geometry.Polygon([ee_coords])
                logger.info("Earth Engine geometry attached to boundary.")
            except Exception as e:
                logger.warning(f"Could not create EE geometry: {e}")
                boundary["ee_geometry"] = None
        else:
            boundary["ee_geometry"] = None

        logger.info(
            f"Boundary created — area={area_hectares:.2f} ha, "
            f"perimeter={perimeter_m:.0f} m, centroid={centroid}"
        )
        return boundary

    @staticmethod
    def _validate_coordinate_list(coords: List[List[float]]):
        """Sanity-check every coordinate pair."""
        for i, coord in enumerate(coords):
            if len(coord) != 2:
                raise ValueError(f"Coordinate {i} must be [lon, lat], got {coord}.")
            lon, lat = coord
            if not (-180 <= lon <= 180):
                raise ValueError(f"Coordinate {i}: longitude {lon} out of range [-180, 180].")
            if not (-90 <= lat <= 90):
                raise ValueError(f"Coordinate {i}: latitude {lat} out of range [-90, 90].")

    @staticmethod
    def _extract_feature(geojson: Dict) -> Dict:
        """Pull a single Feature out of Feature / FeatureCollection / bare Geometry."""
        geojson_type = geojson.get("type", "")

        if geojson_type == "Feature":
            return geojson
        elif geojson_type == "FeatureCollection":
            features = geojson.get("features", [])
            if not features:
                raise ValueError("FeatureCollection contains no features.")
            return features[0]
        elif geojson_type in ("Polygon", "MultiPolygon"):
            # Bare geometry — wrap it
            return {"type": "Feature", "geometry": geojson, "properties": {}}
        else:
            raise ValueError(f"Unrecognised GeoJSON type: {geojson_type}")

    @staticmethod
    def _check_ee() -> bool:
        try:
            from utils.ee_manager import EarthEngineManager
            return EarthEngineManager.is_available()
        except Exception:
            return False
