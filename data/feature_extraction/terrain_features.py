import ee
from typing import Dict
from data.earth_engine.gee_client import GEEClient

class TerrainFeatureExtractor:
    """Extract terrain-related features"""
    
    def __init__(self):
        self.gee_client = GEEClient()
    
    def extract(self, geometry: ee.Geometry) -> Dict:
        """Extract all terrain features"""
        
        # Get elevation data
        elevation = self.gee_client.get_elevation_data(geometry)
        
        # Calculate slope
        slope = self.gee_client.calculate_slope(geometry)
        
        # Calculate aspect (direction of slope)
        aspect = self._calculate_aspect(geometry)
        
        # Determine terrain classification
        terrain_class = self._classify_terrain(slope.get('slope_avg', 0))
        
        return {
            **elevation,
            **slope,
            **aspect,
            'terrain_classification': terrain_class,
            'buildability_score': self._calculate_buildability(slope, elevation),
            'data_quality': 'high'
        }
    
    def _calculate_aspect(self, geometry: ee.Geometry) -> Dict:
        """Calculate terrain aspect (direction)"""
        try:
            srtm = ee.Image('USGS/SRTMGL1_003')
            aspect = ee.Terrain.aspect(srtm)
            
            stats = aspect.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=30,
                maxPixels=1e8
            ).getInfo()
            
            aspect_deg = stats.get('aspect', 0)
            
            return {
                'aspect_degrees': aspect_deg,
                'aspect_direction': self._degrees_to_direction(aspect_deg)
            }
        except Exception as e:
            return {'aspect_degrees': 0, 'aspect_direction': 'N'}
    
    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert degrees to cardinal direction"""
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = int((degrees + 22.5) / 45) % 8
        return directions[index]
    
    def _classify_terrain(self, slope_avg: float) -> str:
        """Classify terrain based on average slope"""
        if slope_avg < 3:
            return 'flat'
        elif slope_avg < 8:
            return 'gentle'
        elif slope_avg < 15:
            return 'moderate'
        elif slope_avg < 30:
            return 'steep'
        else:
            return 'very_steep'
    
    def _calculate_buildability(self, slope: Dict, elevation: Dict) -> float:
        """Calculate buildability score (0-10)"""
        score = 10.0
        
        # Penalize steep slopes
        slope_avg = slope.get('slope_avg', 0)
        if slope_avg > 15:
            score -= (slope_avg - 15) * 0.2
        
        # Penalize high elevation variation
        elev_range = elevation.get('elevation_max', 0) - elevation.get('elevation_min', 0)
        if elev_range > 50:
            score -= (elev_range - 50) * 0.05
        
        return max(0, min(10, score))
