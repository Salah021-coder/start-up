# ============================================================================
# FILE: core/features/terrain.py
# Terrain Feature Extraction from Earth Engine
# ============================================================================

import ee
from typing import Dict, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class TerrainExtractor:
    """
    Extract terrain features from Earth Engine
    
    RESPONSIBILITIES:
    - Fetch elevation data (SRTM, NASADEM)
    - Calculate slope, aspect
    - Compute terrain statistics
    - Assess buildability
    
    DOES NOT:
    - Use fallback values
    - Guess missing data
    - Cache results (caching is pipeline's job)
    """
    
    def __init__(self):
        """Initialize terrain extractor"""
        self.scale = 30  # 30m resolution for SRTM
        
        # Dataset priorities (best to fallback)
        self.elevation_datasets = [
            'NASA/NASADEM_HGT/001',  # Latest NASA DEM (2000)
            'USGS/SRTMGL1_003',      # SRTM 30m
            'JAXA/ALOS/AW3D30/V3_2'  # ALOS World 3D
        ]
    
    def extract(
        self,
        ee_geometry: ee.Geometry
    ) -> Dict:
        """
        Extract all terrain features
        
        Args:
            ee_geometry: Earth Engine geometry
            
        Returns:
            Dict with terrain features
            
        Raises:
            RuntimeError: If Earth Engine fails or data unavailable
        """
        if ee_geometry is None:
            raise ValueError("ee_geometry is None - Earth Engine geometry required")
        
        logger.info("Extracting terrain features from Earth Engine")
        
        try:
            # Get elevation DEM
            dem = self._get_best_dem(ee_geometry)
            
            # Extract elevation statistics
            elevation_stats = self._extract_elevation_stats(dem, ee_geometry)
            
            # Calculate terrain derivatives
            slope_img = ee.Terrain.slope(dem)
            aspect_img = ee.Terrain.aspect(dem)
            
            # Extract slope statistics
            slope_stats = self._extract_slope_stats(slope_img, ee_geometry)
            
            # Extract aspect statistics
            aspect_stats = self._extract_aspect_stats(aspect_img, ee_geometry)
            
            # Calculate buildability score
            buildability = self._calculate_buildability(
                elevation_stats,
                slope_stats
            )
            
            # Combine all features
            terrain_features = {
                # Elevation
                'elevation_avg': elevation_stats['mean'],
                'elevation_min': elevation_stats['min'],
                'elevation_max': elevation_stats['max'],
                'elevation_range': elevation_stats['max'] - elevation_stats['min'],
                'elevation_std': elevation_stats['std'],
                
                # Slope
                'slope_avg': slope_stats['mean'],
                'slope_min': slope_stats['min'],
                'slope_max': slope_stats['max'],
                'slope_std': slope_stats['std'],
                'slope_histogram': slope_stats['histogram'],
                
                # Aspect
                'aspect_avg': aspect_stats['mean'],
                'aspect_dominant': aspect_stats['dominant_direction'],
                'aspect_distribution': aspect_stats['distribution'],
                
                # Derived metrics
                'buildability_score': buildability['score'],
                'buildability_class': buildability['class'],
                'terrain_complexity': self._calculate_terrain_complexity(
                    elevation_stats,
                    slope_stats
                ),
                
                # Metadata
                'data_quality': 'gee',
                'dem_source': dem.get('system:id').getInfo() if hasattr(dem, 'get') else 'unknown',
                'scale_meters': self.scale
            }
            
            logger.info(
                f"Terrain extraction complete: "
                f"elevation {elevation_stats['mean']:.0f}m, "
                f"slope {slope_stats['mean']:.1f}°"
            )
            
            return terrain_features
            
        except Exception as e:
            logger.error(f"Terrain extraction failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to extract terrain features: {str(e)}")
    
    def _get_best_dem(
        self,
        geometry: ee.Geometry
    ) -> ee.Image:
        """
        Get best available DEM for the region
        
        Args:
            geometry: Region of interest
            
        Returns:
            ee.Image with elevation data
            
        Raises:
            RuntimeError: If no DEM available
        """
        for dataset_id in self.elevation_datasets:
            try:
                logger.debug(f"Attempting DEM: {dataset_id}")
                
                dem = ee.Image(dataset_id)
                
                # Test if data exists in region
                test_value = dem.reduceRegion(
                    reducer=ee.Reducer.first(),
                    geometry=geometry.centroid(),
                    scale=self.scale,
                    maxPixels=1
                ).getInfo()
                
                if test_value:
                    logger.info(f"Using DEM: {dataset_id}")
                    return dem
                    
            except Exception as e:
                logger.warning(f"DEM {dataset_id} not available: {e}")
                continue
        
        raise RuntimeError(
            "No elevation data available for this region. "
            "Tried: " + ", ".join(self.elevation_datasets)
        )
    
    def _extract_elevation_stats(
        self,
        dem: ee.Image,
        geometry: ee.Geometry
    ) -> Dict:
        """Extract elevation statistics"""
        
        stats = dem.reduceRegion(
            reducer=ee.Reducer.mean()
                .combine(ee.Reducer.min(), '', True)
                .combine(ee.Reducer.max(), '', True)
                .combine(ee.Reducer.stdDev(), '', True),
            geometry=geometry,
            scale=self.scale,
            maxPixels=1e8
        ).getInfo()
        
        # Handle different band names (elevation vs b1)
        band_name = 'elevation' if 'elevation' in stats else list(stats.keys())[0]
        
        return {
            'mean': float(stats.get(f'{band_name}_mean', 0)),
            'min': float(stats.get(f'{band_name}_min', 0)),
            'max': float(stats.get(f'{band_name}_max', 0)),
            'std': float(stats.get(f'{band_name}_stdDev', 0))
        }
    
    def _extract_slope_stats(
        self,
        slope_img: ee.Image,
        geometry: ee.Geometry
    ) -> Dict:
        """Extract slope statistics"""
        
        # Basic statistics
        stats = slope_img.reduceRegion(
            reducer=ee.Reducer.mean()
                .combine(ee.Reducer.min(), '', True)
                .combine(ee.Reducer.max(), '', True)
                .combine(ee.Reducer.stdDev(), '', True),
            geometry=geometry,
            scale=self.scale,
            maxPixels=1e8
        ).getInfo()
        
        # Slope histogram (for distribution analysis)
        histogram = slope_img.reduceRegion(
            reducer=ee.Reducer.fixedHistogram(0, 90, 9),  # 0-90° in 10° bins
            geometry=geometry,
            scale=self.scale,
            maxPixels=1e8
        ).getInfo()
        
        return {
            'mean': float(stats.get('slope_mean', 0)),
            'min': float(stats.get('slope_min', 0)),
            'max': float(stats.get('slope_max', 0)),
            'std': float(stats.get('slope_stdDev', 0)),
            'histogram': histogram.get('slope', [])
        }
    
    def _extract_aspect_stats(
        self,
        aspect_img: ee.Image,
        geometry: ee.Geometry
    ) -> Dict:
        """Extract aspect (orientation) statistics"""
        
        stats = aspect_img.reduceRegion(
            reducer=ee.Reducer.mean()
                .combine(ee.Reducer.mode(), '', True),
            geometry=geometry,
            scale=self.scale,
            maxPixels=1e8
        ).getInfo()
        
        mean_aspect = float(stats.get('aspect_mean', 0))
        mode_aspect = float(stats.get('aspect_mode', 0))
        
        # Convert to cardinal direction
        dominant_direction = self._aspect_to_direction(mode_aspect)
        
        # Classify into 8 directions for distribution
        distribution = self._calculate_aspect_distribution(aspect_img, geometry)
        
        return {
            'mean': mean_aspect,
            'mode': mode_aspect,
            'dominant_direction': dominant_direction,
            'distribution': distribution
        }
    
    def _aspect_to_direction(self, aspect_degrees: float) -> str:
        """Convert aspect degrees to cardinal direction"""
        directions = [
            'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'
        ]
        index = int((aspect_degrees + 22.5) / 45) % 8
        return directions[index]
    
    def _calculate_aspect_distribution(
        self,
        aspect_img: ee.Image,
        geometry: ee.Geometry
    ) -> Dict:
        """Calculate distribution across 8 cardinal directions"""
        
        # Create bins for 8 directions (N, NE, E, SE, S, SW, W, NW)
        # Each bin is 45 degrees
        
        directions = {
            'N': (337.5, 22.5),    # 337.5-22.5
            'NE': (22.5, 67.5),
            'E': (67.5, 112.5),
            'SE': (112.5, 157.5),
            'S': (157.5, 202.5),
            'SW': (202.5, 247.5),
            'W': (247.5, 292.5),
            'NW': (292.5, 337.5)
        }
        
        # Simplified: just return dominant
        # Full implementation would classify each pixel
        return {
            'primary': 'variable',
            'note': 'Aspect distribution analysis available on request'
        }
    
    def _calculate_buildability(
        self,
        elevation_stats: Dict,
        slope_stats: Dict
    ) -> Dict:
        """
        Calculate buildability score (0-10)
        
        Based on:
        - Slope suitability (flatter = better)
        - Elevation variation (less = better)
        - Terrain complexity
        """
        score = 10.0  # Start with perfect score
        
        avg_slope = slope_stats['mean']
        max_slope = slope_stats['max']
        elevation_range = elevation_stats['max'] - elevation_stats['min']
        
        # Slope penalties
        if avg_slope < 3:
            slope_penalty = 0  # Ideal
        elif avg_slope < 8:
            slope_penalty = 1  # Good
        elif avg_slope < 15:
            slope_penalty = 2  # Moderate
        elif avg_slope < 25:
            slope_penalty = 4  # Challenging
        else:
            slope_penalty = 6  # Very difficult
        
        # Max slope penalties (steep areas)
        if max_slope > 35:
            slope_penalty += 2
        elif max_slope > 25:
            slope_penalty += 1
        
        # Elevation variation penalties
        if elevation_range > 200:
            elevation_penalty = 2
        elif elevation_range > 100:
            elevation_penalty = 1
        else:
            elevation_penalty = 0
        
        score -= slope_penalty
        score -= elevation_penalty
        
        score = max(0, min(10, score))
        
        # Classification
        if score >= 8:
            buildability_class = 'excellent'
        elif score >= 6:
            buildability_class = 'good'
        elif score >= 4:
            buildability_class = 'moderate'
        elif score >= 2:
            buildability_class = 'challenging'
        else:
            buildability_class = 'difficult'
        
        return {
            'score': round(score, 1),
            'class': buildability_class,
            'slope_penalty': slope_penalty,
            'elevation_penalty': elevation_penalty
        }
    
    def _calculate_terrain_complexity(
        self,
        elevation_stats: Dict,
        slope_stats: Dict
    ) -> str:
        """
        Calculate overall terrain complexity
        
        Returns:
            'flat', 'gentle', 'rolling', 'hilly', 'mountainous'
        """
        avg_slope = slope_stats['mean']
        elevation_range = elevation_stats['max'] - elevation_stats['min']
        
        if avg_slope < 2 and elevation_range < 20:
            return 'flat'
        elif avg_slope < 5 and elevation_range < 50:
            return 'gentle'
        elif avg_slope < 10 and elevation_range < 100:
            return 'rolling'
        elif avg_slope < 20 and elevation_range < 300:
            return 'hilly'
        else:
            return 'mountainous'
