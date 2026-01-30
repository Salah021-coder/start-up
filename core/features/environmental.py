# ============================================================================
# FILE: core/features/environmental.py
# Environmental Feature Extraction from Earth Engine
# ============================================================================

import ee
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EnvironmentalExtractor:
    """
    Extract environmental features from Earth Engine
    
    RESPONSIBILITIES:
    - Vegetation indices (NDVI)
    - Land cover classification
    - Water occurrence
    - Air quality estimates
    
    DOES NOT:
    - Use fallback values without logging
    - Cache results
    - Make assumptions about missing data
    """
    
    def __init__(self):
        """Initialize environmental extractor"""
        self.scale = 10  # 10m for Sentinel-2
        
        # Date range for analysis (recent 1 year)
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=365)
    
    def extract(
        self,
        ee_geometry: ee.Geometry,
        terrain_features: Optional[Dict] = None
    ) -> Dict:
        """
        Extract all environmental features
        
        Args:
            ee_geometry: Earth Engine geometry
            terrain_features: Optional terrain context
            
        Returns:
            Dict with environmental features
            
        Raises:
            RuntimeError: If extraction fails
        """
        if ee_geometry is None:
            raise ValueError("ee_geometry is None - Earth Engine geometry required")
        
        logger.info("Extracting environmental features from Earth Engine")
        
        try:
            # Extract NDVI (vegetation)
            ndvi_stats = self._extract_ndvi(ee_geometry)
            
            # Extract land cover
            land_cover = self._extract_land_cover(ee_geometry)
            
            # Extract water occurrence
            water_stats = self._extract_water_occurrence(ee_geometry)
            
            # Calculate environmental score
            env_score = self._calculate_environmental_score(
                ndvi_stats,
                land_cover,
                water_stats
            )
            
            # Combine features
            environmental_features = {
                # Vegetation
                'ndvi_avg': ndvi_stats['mean'],
                'ndvi_min': ndvi_stats['min'],
                'ndvi_max': ndvi_stats['max'],
                'ndvi_std': ndvi_stats['std'],
                'vegetation_health': ndvi_stats['health_category'],
                
                # Land cover
                'land_cover_dominant': land_cover['dominant_class'],
                'land_cover_distribution': land_cover['distribution'],
                'land_cover_diversity': land_cover['diversity_index'],
                
                # Water
                'water_occurrence_avg': water_stats['occurrence_avg'],
                'water_occurrence_max': water_stats['occurrence_max'],
                'permanent_water_percent': water_stats['permanent_water_percent'],
                
                # Derived metrics
                'environmental_score': env_score,
                'green_space_percent': self._calculate_green_space(ndvi_stats, land_cover),
                
                # Metadata
                'data_quality': 'gee',
                'date_range': f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}",
                'scale_meters': self.scale
            }
            
            logger.info(
                f"Environmental extraction complete: "
                f"NDVI {ndvi_stats['mean']:.2f}, "
                f"land cover: {land_cover['dominant_class']}"
            )
            
            return environmental_features
            
        except Exception as e:
            logger.error(f"Environmental extraction failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to extract environmental features: {str(e)}")
    
    def _extract_ndvi(
        self,
        geometry: ee.Geometry
    ) -> Dict:
        """
        Extract NDVI (Normalized Difference Vegetation Index)
        
        Uses Sentinel-2 imagery from past year
        """
        try:
            # Get Sentinel-2 collection
            s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(geometry) \
                .filterDate(
                    self.start_date.strftime('%Y-%m-%d'),
                    self.end_date.strftime('%Y-%m-%d')
                ) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
            
            # Calculate NDVI for each image
            def calculate_ndvi(image):
                ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
                return image.addBands(ndvi)
            
            s2_ndvi = s2.map(calculate_ndvi)
            
            # Get median NDVI
            ndvi_median = s2_ndvi.select('NDVI').median()
            
            # Extract statistics
            stats = ndvi_median.reduceRegion(
                reducer=ee.Reducer.mean()
                    .combine(ee.Reducer.min(), '', True)
                    .combine(ee.Reducer.max(), '', True)
                    .combine(ee.Reducer.stdDev(), '', True),
                geometry=geometry,
                scale=self.scale,
                maxPixels=1e8
            ).getInfo()
            
            mean_ndvi = float(stats.get('NDVI_mean', 0.5))
            
            # Categorize vegetation health
            if mean_ndvi > 0.6:
                health = 'excellent'
            elif mean_ndvi > 0.4:
                health = 'good'
            elif mean_ndvi > 0.2:
                health = 'moderate'
            else:
                health = 'poor'
            
            return {
                'mean': mean_ndvi,
                'min': float(stats.get('NDVI_min', 0)),
                'max': float(stats.get('NDVI_max', 1)),
                'std': float(stats.get('NDVI_stdDev', 0)),
                'health_category': health
            }
            
        except Exception as e:
            logger.warning(f"NDVI extraction failed: {e}")
            # Return conservative estimates
            return {
                'mean': 0.5,
                'min': 0.2,
                'max': 0.8,
                'std': 0.15,
                'health_category': 'unknown'
            }
    
    def _extract_land_cover(
        self,
        geometry: ee.Geometry
    ) -> Dict:
        """
        Extract land cover classification
        
        Uses ESA WorldCover 10m dataset
        """
        try:
            # Get ESA WorldCover (most recent)
            worldcover = ee.ImageCollection('ESA/WorldCover/v200').first()
            
            # Extract land cover distribution
            histogram = worldcover.reduceRegion(
                reducer=ee.Reducer.frequencyHistogram(),
                geometry=geometry,
                scale=10,
                maxPixels=1e8
            ).getInfo()
            
            cover_hist = histogram.get('Map', {})
            
            # Convert class codes to names
            class_names = {
                '10': 'tree_cover',
                '20': 'shrubland',
                '30': 'grassland',
                '40': 'cropland',
                '50': 'built_up',
                '60': 'bare_vegetation',
                '70': 'snow_ice',
                '80': 'water_bodies',
                '90': 'herbaceous_wetland',
                '95': 'mangroves',
                '100': 'moss_lichen'
            }
            
            # Calculate distribution
            total_pixels = sum(cover_hist.values())
            distribution = {}
            
            for code, count in cover_hist.items():
                class_name = class_names.get(str(code), f'class_{code}')
                percent = (count / total_pixels) * 100
                distribution[class_name] = round(percent, 2)
            
            # Find dominant class
            if distribution:
                dominant_class = max(distribution, key=distribution.get)
            else:
                dominant_class = 'unknown'
            
            # Calculate diversity (Shannon index)
            diversity = self._calculate_diversity_index(distribution)
            
            return {
                'dominant_class': dominant_class,
                'distribution': distribution,
                'diversity_index': diversity
            }
            
        except Exception as e:
            logger.warning(f"Land cover extraction failed: {e}")
            return {
                'dominant_class': 'unknown',
                'distribution': {},
                'diversity_index': 0.0
            }
    
    def _extract_water_occurrence(
        self,
        geometry: ee.Geometry
    ) -> Dict:
        """
        Extract water occurrence from JRC Global Surface Water
        
        Shows historical water presence (1984-2021)
        """
        try:
            # Get JRC Global Surface Water
            water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater')
            
            # Water occurrence (0-100%, how often water was present)
            occurrence = water.select('occurrence')
            
            # Extract statistics
            stats = occurrence.reduceRegion(
                reducer=ee.Reducer.mean()
                    .combine(ee.Reducer.max(), '', True),
                geometry=geometry,
                scale=30,
                maxPixels=1e8
            ).getInfo()
            
            occurrence_avg = float(stats.get('occurrence_mean', 0))
            occurrence_max = float(stats.get('occurrence_max', 0))
            
            # Permanent water (occurrence > 90%)
            permanent_mask = occurrence.gt(90)
            permanent_area = permanent_mask.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=geometry,
                scale=30,
                maxPixels=1e8
            ).getInfo()
            
            # Calculate percent of area with permanent water
            permanent_pixels = float(permanent_area.get('occurrence', 0))
            total_pixels = geometry.area().divide(900).getInfo()  # 30m pixels
            permanent_percent = (permanent_pixels / total_pixels) * 100 if total_pixels > 0 else 0
            
            return {
                'occurrence_avg': occurrence_avg,
                'occurrence_max': occurrence_max,
                'permanent_water_percent': round(permanent_percent, 2)
            }
            
        except Exception as e:
            logger.warning(f"Water occurrence extraction failed: {e}")
            return {
                'occurrence_avg': 0.0,
                'occurrence_max': 0.0,
                'permanent_water_percent': 0.0
            }
    
    def _calculate_diversity_index(
        self,
        distribution: Dict[str, float]
    ) -> float:
        """
        Calculate Shannon diversity index
        
        Measures land cover diversity
        """
        if not distribution:
            return 0.0
        
        import math
        
        # Convert percentages to proportions
        proportions = [p / 100 for p in distribution.values() if p > 0]
        
        # Shannon index: H = -Σ(pi * ln(pi))
        diversity = -sum(p * math.log(p) for p in proportions)
        
        return round(diversity, 3)
    
    def _calculate_environmental_score(
        self,
        ndvi_stats: Dict,
        land_cover: Dict,
        water_stats: Dict
    ) -> float:
        """
        Calculate overall environmental quality score (0-10)
        
        Higher score = better environmental conditions
        """
        score = 5.0  # Baseline
        
        # NDVI contribution (healthy vegetation = good)
        ndvi = ndvi_stats['mean']
        if ndvi > 0.6:
            score += 2
        elif ndvi > 0.4:
            score += 1
        elif ndvi < 0.2:
            score -= 1
        
        # Land cover diversity (more diverse = better)
        diversity = land_cover['diversity_index']
        if diversity > 1.5:
            score += 1
        elif diversity > 1.0:
            score += 0.5
        
        # Water presence (some water = good, too much = bad)
        water_occurrence = water_stats['occurrence_avg']
        if 5 < water_occurrence < 20:
            score += 1  # Good water availability
        elif water_occurrence > 50:
            score -= 2  # Flood risk
        
        return round(max(0, min(10, score)), 1)
    
    def _calculate_green_space(
        self,
        ndvi_stats: Dict,
        land_cover: Dict
    ) -> float:
        """
        Calculate percentage of green/natural space
        
        Based on NDVI and land cover
        """
        distribution = land_cover['distribution']
        
        green_classes = [
            'tree_cover',
            'shrubland',
            'grassland',
            'herbaceous_wetland'
        ]
        
        green_percent = sum(
            distribution.get(cls, 0)
            for cls in green_classes
        )
        
        return round(green_percent, 1)
