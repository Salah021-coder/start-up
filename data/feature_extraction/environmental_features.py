import ee
from typing import Dict
from data.earth_engine.gee_client import GEEClient

class EnvironmentalFeatureExtractor:
    """Extract environmental features"""
    
    def __init__(self):
        self.gee_client = GEEClient()
    
    def extract(self, geometry: ee.Geometry) -> Dict:
        """Extract all environmental features"""
        
        # Get vegetation index
        ndvi = self.gee_client.get_ndvi(geometry)
        
        # Get land cover
        land_cover = self.gee_client.get_land_cover(geometry)
        
        # Get water occurrence (flood risk indicator)
        water = self.gee_client.get_water_occurrence(geometry)
        
        # Calculate flood risk
        flood_risk = self._assess_flood_risk(water, geometry)
        
        # Get air quality estimate (simplified)
        air_quality = self._estimate_air_quality(land_cover)
        
        return {
            **ndvi,
            **land_cover,
            **water,
            'flood_risk_level': flood_risk['level'],
            'flood_risk_percent': flood_risk['percent'],
            'air_quality_estimate': air_quality,
            'environmental_score': self._calculate_env_score(ndvi, flood_risk),
            'data_quality': 'high'
        }
    
    def _assess_flood_risk(self, water_data: Dict, geometry: ee.Geometry) -> Dict:
        """Assess flood risk based on water occurrence"""
        occurrence = water_data.get('water_occurrence_avg', 0)
        
        if occurrence < 10:
            level = 'low'
        elif occurrence < 30:
            level = 'medium'
        else:
            level = 'high'
        
        return {
            'level': level,
            'percent': occurrence
        }
    
    def _estimate_air_quality(self, land_cover: Dict) -> str:
        """Estimate air quality based on land cover"""
        dominant = land_cover.get('dominant_cover', 'unknown')
        
        if dominant in ['tree_cover', 'grassland', 'wetland']:
            return 'good'
        elif dominant in ['cropland', 'shrubland']:
            return 'moderate'
        elif dominant in ['built_up', 'industrial']:
            return 'poor'
        else:
            return 'unknown'
    
    def _calculate_env_score(self, ndvi: Dict, flood_risk: Dict) -> float:
        """Calculate overall environmental score"""
        score = 5.0
        
        # Good vegetation increases score
        ndvi_val = ndvi.get('ndvi_avg', 0)
        score += (ndvi_val - 0.3) * 5
        
        # Flood risk decreases score
        if flood_risk['level'] == 'low':
            score += 2
        elif flood_risk['level'] == 'high':
            score -= 2
        
        return max(0, min(10, score))
