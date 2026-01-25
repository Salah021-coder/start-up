import ee
from config.gee_config import GEEConfig
from typing import Dict, Optional
import numpy as np

class GEEClient:
    """Google Earth Engine API Client"""
    
    def __init__(self):
        GEEConfig.initialize()
        self.config = GEEConfig()
    
    def get_elevation_data(self, geometry: ee.Geometry) -> Dict:
        """Get elevation data using SRTM"""
        try:
            srtm = ee.Image(self.config.DATASETS['elevation']['srtm'])
            
            stats = srtm.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.minMax(), '', True
                ).combine(
                    ee.Reducer.stdDev(), '', True
                ),
                geometry=geometry,
                scale=self.config.SCALE,
                maxPixels=self.config.MAX_PIXELS
            ).getInfo()
            
            return {
                'elevation_avg': stats.get('elevation_mean', 0),
                'elevation_min': stats.get('elevation_min', 0),
                'elevation_max': stats.get('elevation_max', 0),
                'elevation_std': stats.get('elevation_stdDev', 0)
            }
        except Exception as e:
            print(f"Error getting elevation data: {e}")
            return {}
    
    def calculate_slope(self, geometry: ee.Geometry) -> Dict:
        """Calculate slope from elevation data"""
        try:
            srtm = ee.Image(self.config.DATASETS['elevation']['srtm'])
            slope = ee.Terrain.slope(srtm)
            
            stats = slope.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.minMax(), '', True
                ),
                geometry=geometry,
                scale=self.config.SCALE,
                maxPixels=self.config.MAX_PIXELS
            ).getInfo()
            
            return {
                'slope_avg': stats.get('slope_mean', 0),
                'slope_min': stats.get('slope_min', 0),
                'slope_max': stats.get('slope_max', 0)
            }
        except Exception as e:
            print(f"Error calculating slope: {e}")
            return {}
    
    def get_ndvi(self, geometry: ee.Geometry, date_range: Dict = None) -> Dict:
        """Calculate NDVI (vegetation index) from Sentinel-2"""
        try:
            if not date_range:
                date_range = self.config.DEFAULT_DATE_RANGE
            
            sentinel = ee.ImageCollection(self.config.DATASETS['vegetation']['sentinel2']) \
                .filterDate(date_range['start'], date_range['end']) \
                .filterBounds(geometry) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
            
            def add_ndvi(image):
                ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
                return image.addBands(ndvi)
            
            with_ndvi = sentinel.map(add_ndvi)
            ndvi_median = with_ndvi.select('NDVI').median()
            
            stats = ndvi_median.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.minMax(), '', True
                ),
                geometry=geometry,
                scale=self.config.SCALE,
                maxPixels=self.config.MAX_PIXELS
            ).getInfo()
            
            return {
                'ndvi_avg': stats.get('NDVI_mean', 0),
                'ndvi_min': stats.get('NDVI_min', 0),
                'ndvi_max': stats.get('NDVI_max', 0)
            }
        except Exception as e:
            print(f"Error calculating NDVI: {e}")
            return {'ndvi_avg': 0.5, 'ndvi_min': 0, 'ndvi_max': 1}
    
    def get_land_cover(self, geometry: ee.Geometry) -> Dict:
        """Get land cover classification"""
        try:
            worldcover = ee.ImageCollection(
                self.config.DATASETS['land_cover']['esa_worldcover']
            ).first()
            
            # Get land cover distribution
            cover_stats = worldcover.reduceRegion(
                reducer=ee.Reducer.frequencyHistogram(),
                geometry=geometry,
                scale=self.config.SCALE,
                maxPixels=self.config.MAX_PIXELS
            ).getInfo()
            
            return {
                'land_cover_distribution': cover_stats.get('Map', {}),
                'dominant_cover': self._get_dominant_cover(cover_stats.get('Map', {}))
            }
        except Exception as e:
            print(f"Error getting land cover: {e}")
            return {}
    
    def get_water_occurrence(self, geometry: ee.Geometry) -> Dict:
        """Get water occurrence data"""
        try:
            water = ee.Image(self.config.DATASETS['water']['jrc_water'])
            occurrence = water.select('occurrence')
            
            stats = occurrence.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.max(), '', True
                ),
                geometry=geometry,
                scale=self.config.SCALE,
                maxPixels=self.config.MAX_PIXELS
            ).getInfo()
            
            return {
                'water_occurrence_avg': stats.get('occurrence_mean', 0),
                'water_occurrence_max': stats.get('occurrence_max', 0)
            }
        except Exception as e:
            print(f"Error getting water data: {e}")
            return {}
    
    def _get_dominant_cover(self, distribution: Dict) -> str:
        """Get dominant land cover type"""
        if not distribution:
            return 'unknown'
        
        cover_types = {
            '10': 'tree_cover',
            '20': 'shrubland',
            '30': 'grassland',
            '40': 'cropland',
            '50': 'built_up',
            '60': 'bare',
            '70': 'snow_ice',
            '80': 'water',
            '90': 'wetland',
            '95': 'mangroves'
        }
        
        max_key = max(distribution, key=distribution.get)
        return cover_types.get(str(max_key), 'unknown')