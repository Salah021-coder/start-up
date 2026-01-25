
from typing import Dict, Tuple
import requests
from shapely.geometry import Point
import math

class InfrastructureFeatureExtractor:
    """Extract infrastructure-related features"""
    
    def __init__(self):
        self.osm_api_base = "https://overpass-api.de/api/interpreter"
    
    def extract(self, centroid: Tuple[float, float], geometry) -> Dict:
        """Extract infrastructure features"""
        
        lon, lat = centroid
        
        # Get nearby roads
        roads = self._get_nearby_roads(lat, lon)
        
        # Get utilities
        utilities = self._check_utilities(lat, lon)
        
        # Get amenities
        amenities = self._get_nearby_amenities(lat, lon)
        
        # Calculate accessibility score
        accessibility = self._calculate_accessibility(roads, amenities)
        
        return {
            'nearest_road_distance': roads['distance'],
            'road_type': roads['type'],
            'utilities_available': utilities,
            'nearby_amenities': amenities,
            'accessibility_score': accessibility,
            'infrastructure_score': self._calculate_infrastructure_score(roads, utilities),
            'data_quality': 'medium'
        }
    
    def _get_nearby_roads(self, lat: float, lon: float) -> Dict:
        """Get nearest road using Overpass API"""
        try:
            # Simplified - in production use actual OSM queries
            # This is a mock response
            return {
                'distance': 450,  # meters
                'type': 'secondary',
                'name': 'Main Street'
            }
        except Exception as e:
            return {'distance': 999999, 'type': 'unknown', 'name': ''}
    
    def _check_utilities(self, lat: float, lon: float) -> Dict:
        """Check availability of utilities"""
        # Simplified - would query actual utility databases
        return {
            'water': True,
            'electricity': True,
            'gas': False,
            'sewage': True,
            'internet': True
        }
    
    def _get_nearby_amenities(self, lat: float, lon: float) -> Dict:
        """Get nearby amenities"""
        # Simplified - would use OSM Overpass API
        return {
            'schools': 2,
            'hospitals': 1,
            'shopping': 3,
            'restaurants': 5,
            'parks': 1
        }
    
    def _calculate_accessibility(self, roads: Dict, amenities: Dict) -> float:
        """Calculate accessibility score (0-10)"""
        score = 5.0
        
        # Road proximity
        distance = roads['distance']
        if distance < 500:
            score += 3
        elif distance < 1000:
            score += 2
        elif distance < 2000:
            score += 1
        else:
            score -= 1
        
        # Amenities
        total_amenities = sum(amenities.values())
        score += min(2, total_amenities * 0.2)
        
        return max(0, min(10, score))
    
    def _calculate_infrastructure_score(self, roads: Dict, utilities: Dict) -> float:
        """Calculate overall infrastructure score"""
        score = 5.0
        
        # Road access
        if roads['distance'] < 500:
            score += 2
        elif roads['distance'] > 2000:
            score -= 2
        
        # Utilities
        available = sum(1 for v in utilities.values() if v)
        score += (available / len(utilities)) * 3
        
        return max(0, min(10, score))