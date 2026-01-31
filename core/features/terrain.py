# ============================================================================
# FILE: core/features/terrain.py
# Terrain Feature Extraction from Earth Engine
# ============================================================================

import ee
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class TerrainExtractor:
    """
    Extract terrain features from Earth Engine
    """

    def __init__(self):
        self.scale = 30  # meters

        self.elevation_datasets = [
            "NASA/NASADEM_HGT/001",
            "USGS/SRTMGL1_003",
            "JAXA/ALOS/AW3D30/V3_2",
        ]

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def extract(self, ee_geometry: ee.Geometry) -> Dict:
        if ee_geometry is None:
            raise ValueError("Earth Engine geometry is required")

        try:
            dem = self._get_best_dem(ee_geometry)

            elevation_stats = self._extract_elevation_stats(dem, ee_geometry)

            slope_img = ee.Terrain.slope(dem)
            aspect_img = ee.Terrain.aspect(dem)

            slope_stats = self._extract_slope_stats(slope_img, ee_geometry)
            aspect_stats = self._extract_aspect_stats(aspect_img, ee_geometry)

            buildability = self._calculate_buildability(
                elevation_stats, slope_stats
            )

            return {
                # Elevation
                "elevation_avg": elevation_stats["mean"],
                "elevation_min": elevation_stats["min"],
                "elevation_max": elevation_stats["max"],
                "elevation_range": elevation_stats["max"]
                - elevation_stats["min"],
                "elevation_std": elevation_stats["std"],

                # Slope
                "slope_avg": slope_stats["mean"],
                "slope_min": slope_stats["min"],
                "slope_max": slope_stats["max"],
                "slope_std": slope_stats["std"],
                "slope_histogram": slope_stats["histogram"],

                # Aspect
                "aspect_avg": aspect_stats["mean"],
                "aspect_dominant": aspect_stats["dominant_direction"],
                "aspect_distribution": aspect_stats["distribution"],

                # Derived
                "buildability_score": buildability["score"],
                "buildability_class": buildability["class"],
                "terrain_complexity": self._calculate_terrain_complexity(
                    elevation_stats, slope_stats
                ),

                # Metadata
                "data_quality": "gee",
                "dem_source": dem.get("system:id").getInfo(),
                "scale_meters": self.scale,
            }

        except Exception as e:
            logger.exception("Terrain extraction failed")
            raise RuntimeError(f"Terrain extraction failed: {e}")

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _get_best_dem(self, geometry: ee.Geometry) -> ee.Image:
        for dataset_id in self.elevation_datasets:
            try:
                dem = ee.Image(dataset_id)

                test = dem.reduceRegion(
                    ee.Reducer.first(),
                    geometry.centroid(),
                    self.scale,
                    maxPixels=1,
                ).getInfo()

                if test:
                    logger.info(f"Using DEM: {dataset_id}")
                    return dem

            except Exception:
                continue

        raise RuntimeError("No DEM available for this region")

    def _extract_elevation_stats(
        self, dem: ee.Image, geometry: ee.Geometry
    ) -> Dict:
        stats = dem.reduceRegion(
            ee.Reducer.mean()
            .combine(ee.Reducer.min(), "", True)
            .combine(ee.Reducer.max(), "", True)
            .combine(ee.Reducer.stdDev(), "", True),
            geometry,
            self.scale,
            maxPixels=1e8,
        ).getInfo()

        band = "elevation" if "elevation_mean" in stats else list(stats.keys())[0].split("_")[0]

        return {
            "mean": float(stats.get(f"{band}_mean", 0)),
            "min": float(stats.get(f"{band}_min", 0)),
            "max": float(stats.get(f"{band}_max", 0)),
            "std": float(stats.get(f"{band}_stdDev", 0)),
        }

    def _extract_slope_stats(
        self, slope_img: ee.Image, geometry: ee.Geometry
    ) -> Dict:
        stats = slope_img.reduceRegion(
            ee.Reducer.mean()
            .combine(ee.Reducer.min(), "", True)
            .combine(ee.Reducer.max(), "", True)
            .combine(ee.Reducer.stdDev(), "", True),
            geometry,
            self.scale,
            maxPixels=1e8,
        ).getInfo()

        hist_raw = slope_img.reduceRegion(
            ee.Reducer.fixedHistogram(0, 90, 9),
            geometry,
            self.scale,
            maxPixels=1e8,
        ).getInfo()

        raw = hist_raw.get("slope", [])
        histogram = []

        # ---- CRITICAL FIX ----
        if isinstance(raw, tuple) and len(raw) == 2:
            bucket_means, counts = raw
            histogram = [
                {"slope_deg": float(b), "count": int(c)}
                for b, c in zip(bucket_means, counts)
            ]
        elif isinstance(raw, list):
            histogram = raw
        # ---------------------

        return {
            "mean": float(stats.get("slope_mean", 0)),
            "min": float(stats.get("slope_min", 0)),
            "max": float(stats.get("slope_max", 0)),
            "std": float(stats.get("slope_stdDev", 0)),
            "histogram": histogram,
        }

    def _extract_aspect_stats(
        self, aspect_img: ee.Image, geometry: ee.Geometry
    ) -> Dict:
        stats = aspect_img.reduceRegion(
            ee.Reducer.mean().combine(ee.Reducer.mode(), "", True),
            geometry,
            self.scale,
            maxPixels=1e8,
        ).getInfo()

        mean = float(stats.get("aspect_mean", 0))
        mode = float(stats.get("aspect_mode", 0))

        return {
            "mean": mean,
            "mode": mode,
            "dominant_direction": self._aspect_to_direction(mode),
            "distribution": {"note": "Simplified"},
        }

    def _aspect_to_direction(self, deg: float) -> str:
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
        idx = int((deg + 22.5) / 45) % 8
        return directions[idx]

    def _calculate_buildability(
        self, elevation: Dict, slope: Dict
    ) -> Dict:
        score = 10.0

        avg_slope = slope["mean"]
        max_slope = slope["max"]
        elev_range = elevation["max"] - elevation["min"]

        if avg_slope >= 25:
            score -= 6
        elif avg_slope >= 15:
            score -= 4
        elif avg_slope >= 8:
            score -= 2
        elif avg_slope >= 3:
            score -= 1

        if max_slope > 35:
            score -= 2
        elif max_slope > 25:
            score -= 1

        if elev_range > 200:
            score -= 2
        elif elev_range > 100:
            score -= 1

        score = max(0, min(10, score))

        if score >= 8:
            cls = "excellent"
        elif score >= 6:
            cls = "good"
        elif score >= 4:
            cls = "moderate"
        elif score >= 2:
            cls = "challenging"
        else:
            cls = "difficult"

        return {"score": round(score, 1), "class": cls}

    def _calculate_terrain_complexity(
        self, elevation: Dict, slope: Dict
    ) -> str:
        avg_slope = slope["mean"]
        elev_range = elevation["max"] - elevation["min"]

        if avg_slope < 2 and elev_range < 20:
            return "flat"
        elif avg_slope < 5 and elev_range < 50:
            return "gentle"
        elif avg_slope < 10 and elev_range < 100:
            return "rolling"
        elif avg_slope < 20 and elev_range < 300:
            return "hilly"
        else:
            return "mountainous"
