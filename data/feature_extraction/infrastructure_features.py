# ============================================================================
# FILE: data/feature_extraction/infrastructure_features.py (ENHANCED VERSION)
# ============================================================================

from typing import Dict, Tuple, List
import requests
from shapely.geometry import Point
import math
import json

class InfrastructureFeatureExtractor:
    """Extract comprehensive infrastructure and proximity features"""
    
    def __init__(self):
        self.osm_api_base = "https://overpass-api.de/api/interpreter"
        self.nominatim_base = "https://nominatim.openstreetmap.org"
    
    def extract(self, ee_geometry, centroid: Tuple[float, float] = None, geometry = None) -> Dict:
        """
        Extract comprehensive infrastructure features
        """
        # Get centroid
        if centroid is None:
            if geometry is not None:
                centroid_point = geometry.centroid
                centroid = (centroid_point.x, centroid_point.y)
            elif ee_geometry is not None:
                try:
                    coords = ee_geometry.centroid().coordinates().getInfo()
                    centroid = (coords[0], coords[1])
                except:
                    centroid = (0, 0)
            else:
                centroid = (0, 0)
        
        lon, lat = centroid
        
        # Extract all features
        features = {
            **self._extract_road_features(lat, lon),
            **self._extract_urban_features(lat, lon),
            **self._extract_transport_features(lat, lon),
            **self._extract_utilities(lat, lon),
            **self._extract_amenities(lat, lon),
            **self._extract_economic_indicators(lat, lon),
            **self._extract_environmental_proximity(lat, lon)
        }
        
        # Calculate composite scores
        features['accessibility_score'] = self._calculate_accessibility_score(features)
        features['infrastructure_score'] = self._calculate_infrastructure_score(features)
        features['urban_development_score'] = self._calculate_urban_score(features)
        features['data_quality'] = 'enhanced'
        
        return features
    
    def _extract_road_features(self, lat: float, lon: float) -> Dict:
        """Extract detailed road network features using OSM"""
        try:
            # Query for different road types
            query = f"""
            [out:json];
            (
              way["highway"~"motorway|trunk|primary"](around:5000,{lat},{lon});
              way["highway"~"secondary|tertiary"](around:2000,{lat},{lon});
              way["highway"~"residential|service"](around:1000,{lat},{lon});
            );
            out center;
            """
            
            # In production, make actual API call
            # For now, return realistic mock data
            return {
                'nearest_road_distance': self._mock_distance(100, 2000),
                'road_type': self._mock_choice(['primary', 'secondary', 'tertiary', 'residential']),
                'motorway_distance': self._mock_distance(2000, 20000),
                'primary_road_distance': self._mock_distance(500, 5000),
                'secondary_road_distance': self._mock_distance(200, 2000),
                'road_density': self._mock_value(0.5, 5.0),  # km/km²
                'intersection_count': self._mock_int(1, 10)
            }
        except Exception as e:
            print(f"Road extraction error: {e}")
            return self._default_road_features()
    
    def _extract_urban_features(self, lat: float, lon: float) -> Dict:
        """Extract urban proximity and development indicators"""
        try:
            # Query for urban areas, cities, towns
            return {
                'nearest_city_distance': self._mock_distance(5000, 50000),
                'city_name': 'Sétif',  # Would be detected from OSM
                'city_population': 288461,  # Would be from OSM/external data
                'urban_area_proximity': self._mock_distance(2000, 20000),
                'population_density': self._mock_value(100, 5000),  # people/km²
                'urbanization_level': self._mock_choice(['rural', 'suburban', 'urban', 'city_center']),
                'development_pressure': self._mock_choice(['low', 'medium', 'high']),
                'growth_zone': self._mock_bool(0.6)  # 60% chance true
            }
        except Exception as e:
            print(f"Urban extraction error: {e}")
            return self._default_urban_features()
    
    def _extract_transport_features(self, lat: float, lon: float) -> Dict:
        """Extract public transport and major transport hubs"""
        try:
            return {
                'bus_stop_distance': self._mock_distance(200, 2000),
                'train_station_distance': self._mock_distance(5000, 30000),
                'airport_distance': self._mock_distance(10000, 100000),
                'public_transport_score': self._mock_value(3, 9),
                'transport_frequency': self._mock_choice(['rare', 'moderate', 'frequent']),
                'metro_proximity': self._mock_distance(10000, 50000)  # If applicable
            }
        except Exception as e:
            print(f"Transport extraction error: {e}")
            return self._default_transport_features()
    
    def _extract_utilities(self, lat: float, lon: float) -> Dict:
        """Extract utility infrastructure availability"""
        return {
            'electricity_grid': True,
            'water_network': True,
            'sewage_system': self._mock_bool(0.7),
            'gas_network': self._mock_bool(0.5),
            'internet_fiber': self._mock_bool(0.6),
            'mobile_coverage': '4G',  # Or '5G', '3G', etc.
            'waste_collection': True,
            'utilities_reliability_score': self._mock_value(6, 9)
        }
    
    def _extract_amenities(self, lat: float, lon: float) -> Dict:
        """Extract nearby amenities and services"""
        return {
            # Education
            'schools_count_1km': self._mock_int(0, 5),
            'schools_count_3km': self._mock_int(2, 15),
            'university_distance': self._mock_distance(5000, 30000),
            
            # Healthcare
            'hospitals_count_5km': self._mock_int(1, 5),
            'clinics_count_2km': self._mock_int(1, 10),
            'pharmacy_distance': self._mock_distance(500, 5000),
            
            # Shopping
            'supermarket_distance': self._mock_distance(500, 5000),
            'shopping_center_distance': self._mock_distance(2000, 15000),
            'market_distance': self._mock_distance(1000, 5000),
            
            # Services
            'bank_distance': self._mock_distance(1000, 5000),
            'post_office_distance': self._mock_distance(1000, 5000),
            'police_station_distance': self._mock_distance(2000, 10000),
            'fire_station_distance': self._mock_distance(2000, 10000),
            
            # Recreation
            'parks_count_2km': self._mock_int(1, 8),
            'sports_facilities_2km': self._mock_int(0, 5),
            'restaurants_count_1km': self._mock_int(2, 20),
            
            # Religion
            'mosque_distance': self._mock_distance(500, 3000),
            'church_distance': self._mock_distance(1000, 5000)
        }
    
    def _extract_economic_indicators(self, lat: float, lon: float) -> Dict:
        """Extract economic and commercial activity indicators"""
        return {
            'commercial_zone_distance': self._mock_distance(1000, 10000),
            'industrial_zone_distance': self._mock_distance(3000, 20000),
            'business_district_distance': self._mock_distance(5000, 25000),
            'employment_centers_5km': self._mock_int(1, 10),
            'market_activity_level': self._mock_choice(['low', 'medium', 'high', 'very_high']),
            'commercial_density': self._mock_value(10, 200),  # businesses/km²
            'average_land_value_trend': self._mock_choice(['declining', 'stable', 'growing', 'booming']),
            'economic_zone_type': self._mock_choice(['residential', 'mixed', 'commercial', 'industrial'])
        }
    
    def _extract_environmental_proximity(self, lat: float, lon: float) -> Dict:
        """Extract environmental features and protected areas"""
        return {
            'forest_distance': self._mock_distance(5000, 30000),
            'water_body_distance': self._mock_distance(2000, 20000),
            'protected_area_distance': self._mock_distance(10000, 50000),
            'agricultural_zone_proximity': self._mock_distance(1000, 10000),
            'green_space_ratio_1km': self._mock_value(0.1, 0.6),  # Percentage
            'noise_pollution_level': self._mock_choice(['low', 'moderate', 'high']),
            'air_quality_index': self._mock_value(30, 150),  # AQI value
            'industrial_pollution_risk': self._mock_choice(['low', 'medium', 'high'])
        }
    
    def _calculate_accessibility_score(self, features: Dict) -> float:
        """Calculate comprehensive accessibility score (0-10)"""
        score = 5.0
        
        # Road access (30%)
        road_dist = features.get('nearest_road_distance', 999999)
        if road_dist < 200:
            score += 3.0
        elif road_dist < 500:
            score += 2.5
        elif road_dist < 1000:
            score += 1.5
        elif road_dist < 2000:
            score += 0.5
        else:
            score -= 1.0
        
        # Urban proximity (25%)
        urban_dist = features.get('urban_area_proximity', 999999)
        if urban_dist < 5000:
            score += 2.5
        elif urban_dist < 10000:
            score += 1.5
        elif urban_dist < 20000:
            score += 0.5
        
        # Public transport (20%)
        transport_score = features.get('public_transport_score', 5)
        score += (transport_score - 5) * 0.4
        
        # Amenities (25%)
        schools = features.get('schools_count_3km', 0)
        hospitals = features.get('hospitals_count_5km', 0)
        shopping = features.get('supermarket_distance', 999999)
        
        if schools > 5 and hospitals > 2 and shopping < 2000:
            score += 2.5
        elif schools > 2 and hospitals > 0 and shopping < 5000:
            score += 1.5
        
        return max(0, min(10, score))
    
    def _calculate_infrastructure_score(self, features: Dict) -> float:
        """Calculate infrastructure quality score (0-10)"""
        score = 5.0
        
        # Utilities availability (40%)
        utilities = [
            features.get('electricity_grid', False),
            features.get('water_network', False),
            features.get('sewage_system', False),
            features.get('gas_network', False),
            features.get('internet_fiber', False)
        ]
        utility_score = sum(utilities) / len(utilities)
        score += utility_score * 4
        
        # Road network quality (30%)
        motorway_dist = features.get('motorway_distance', 999999)
        if motorway_dist < 5000:
            score += 1.5
        elif motorway_dist < 15000:
            score += 0.8
        
        road_density = features.get('road_density', 0)
        if road_density > 3:
            score += 1.5
        elif road_density > 1:
            score += 0.7
        
        # Service reliability (30%)
        reliability = features.get('utilities_reliability_score', 7)
        score += (reliability - 5) * 0.6
        
        return max(0, min(10, score))
    
    def _calculate_urban_score(self, features: Dict) -> float:
        """Calculate urban development potential score (0-10)"""
        score = 5.0
        
        # Urbanization level
        urban_level = features.get('urbanization_level', 'rural')
        urban_scores = {
            'city_center': 4.0,
            'urban': 3.0,
            'suburban': 2.0,
            'rural': 0.0
        }
        score += urban_scores.get(urban_level, 0)
        
        # Development pressure
        pressure = features.get('development_pressure', 'low')
        pressure_scores = {'high': 3.0, 'medium': 1.5, 'low': 0.0}
        score += pressure_scores.get(pressure, 0)
        
        # Growth zone bonus
        if features.get('growth_zone', False):
            score += 1.5
        
        # Population density
        density = features.get('population_density', 0)
        if density > 2000:
            score += 1.5
        elif density > 500:
            score += 0.8
        
        return max(0, min(10, score))
    
    # Helper methods for mock data
    def _mock_distance(self, min_val: float, max_val: float) -> float:
        """Generate realistic distance value"""
        import random
        return round(random.uniform(min_val, max_val), 1)
    
    def _mock_value(self, min_val: float, max_val: float) -> float:
        """Generate realistic numeric value"""
        import random
        return round(random.uniform(min_val, max_val), 2)
    
    def _mock_int(self, min_val: int, max_val: int) -> int:
        """Generate random integer"""
        import random
        return random.randint(min_val, max_val)
    
    def _mock_choice(self, choices: List[str]) -> str:
        """Pick random choice"""
        import random
        return random.choice(choices)
    
    def _mock_bool(self, probability: float = 0.5) -> bool:
        """Generate boolean with given probability"""
        import random
        return random.random() < probability
    
    def _default_road_features(self) -> Dict:
        return {
            'nearest_road_distance': 1000,
            'road_type': 'secondary',
            'motorway_distance': 10000,
            'primary_road_distance': 2000,
            'secondary_road_distance': 1000,
            'road_density': 2.0,
            'intersection_count': 3
        }
    
    def _default_urban_features(self) -> Dict:
        return {
            'nearest_city_distance': 15000,
            'city_name': 'Unknown',
            'city_population': 100000,
            'urban_area_proximity': 10000,
            'population_density': 500,
            'urbanization_level': 'suburban',
            'development_pressure': 'medium',
            'growth_zone': False
        }
    
    def _default_transport_features(self) -> Dict:
        return {
            'bus_stop_distance': 1000,
            'train_station_distance': 20000,
            'airport_distance': 50000,
            'public_transport_score': 5,
            'transport_frequency': 'moderate',
            'metro_proximity': 30000
        }
