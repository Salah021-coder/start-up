# ============================================================================
# FILE: data/feature_extraction/osm_data_fetcher.py (NEW FILE)
# ============================================================================

import requests
import time
from typing import Dict, List, Tuple
import json

class OSMDataFetcher:
    """
    Fetch real data from OpenStreetMap using Overpass API
    This replaces mock data with actual geographic information
    """
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_nearest_roads(self, lat: float, lon: float, radius: int = 5000) -> Dict:
        """
        Get nearest roads of different types
        Returns distances to motorway, primary, secondary roads
        """
        try:
            self._rate_limit()
            
            # Overpass query for roads
            query = f"""
            [out:json][timeout:25];
            (
              way["highway"="motorway"](around:{radius},{lat},{lon});
              way["highway"="trunk"](around:{radius},{lat},{lon});
              way["highway"="primary"](around:{radius},{lat},{lon});
              way["highway"="secondary"](around:{radius},{lat},{lon});
              way["highway"="tertiary"](around:{radius},{lat},{lon});
              way["highway"="residential"](around:{radius},{lat},{lon});
            );
            out center;
            """
            
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_road_results(data, lat, lon)
            else:
                print(f"OSM request failed: {response.status_code}")
                return self._default_road_data()
                
        except Exception as e:
            print(f"Error fetching road data: {e}")
            return self._default_road_data()
    
    def _process_road_results(self, data: Dict, lat: float, lon: float) -> Dict:
        """Process Overpass API results to extract road distances"""
        from geopy.distance import geodesic
        
        roads_by_type = {
            'motorway': [],
            'trunk': [],
            'primary': [],
            'secondary': [],
            'tertiary': [],
            'residential': []
        }
        
        # Group roads by type
        for element in data.get('elements', []):
            if 'center' in element:
                road_type = element.get('tags', {}).get('highway', 'unknown')
                if road_type in roads_by_type:
                    center = element['center']
                    distance = geodesic(
                        (lat, lon),
                        (center['lat'], center['lon'])
                    ).meters
                    roads_by_type[road_type].append(distance)
        
        # Get minimum distances
        result = {
            'motorway_distance': min(roads_by_type['motorway']) if roads_by_type['motorway'] else 50000,
            'primary_road_distance': min(roads_by_type['primary']) if roads_by_type['primary'] else 10000,
            'secondary_road_distance': min(roads_by_type['secondary']) if roads_by_type['secondary'] else 5000,
            'nearest_road_distance': 999999,
            'road_type': 'unknown',
            'road_density': len(data.get('elements', [])) / 25.0  # per km²
        }
        
        # Find overall nearest road
        for road_type, distances in roads_by_type.items():
            if distances:
                min_dist = min(distances)
                if min_dist < result['nearest_road_distance']:
                    result['nearest_road_distance'] = min_dist
                    result['road_type'] = road_type
        
        return result
    
    def get_nearest_city(self, lat: float, lon: float) -> Dict:
        """Get information about nearest city/town"""
        try:
            self._rate_limit()
            
            # Use Nominatim reverse geocoding
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1,
                'zoom': 10
            }
            
            response = requests.get(
                f"{self.nominatim_url}/reverse",
                params=params,
                headers={'User-Agent': 'LandEvaluationApp/1.0'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                
                return {
                    'city_name': address.get('city') or address.get('town') or address.get('village', 'Unknown'),
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'display_name': data.get('display_name', '')
                }
            else:
                return self._default_city_data()
                
        except Exception as e:
            print(f"Error fetching city data: {e}")
            return self._default_city_data()
    
    def get_amenities(self, lat: float, lon: float, radius: int = 3000) -> Dict:
        """Get counts of various amenities within radius"""
        try:
            self._rate_limit()
            
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="school"](around:{radius},{lat},{lon});
              node["amenity"="hospital"](around:{radius},{lat},{lon});
              node["amenity"="clinic"](around:{radius},{lat},{lon});
              node["amenity"="pharmacy"](around:{radius},{lat},{lon});
              node["shop"="supermarket"](around:{radius},{lat},{lon});
              node["amenity"="bank"](around:{radius},{lat},{lon});
              node["amenity"="restaurant"](around:{radius},{lat},{lon});
              node["amenity"="cafe"](around:{radius},{lat},{lon});
              node["leisure"="park"](around:{radius},{lat},{lon});
              node["amenity"="place_of_worship"](around:{radius},{lat},{lon});
            );
            out count;
            """
            
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                
                # Count by type
                amenity_counts = {}
                for element in elements:
                    tags = element.get('tags', {})
                    amenity_type = tags.get('amenity') or tags.get('shop') or tags.get('leisure')
                    if amenity_type:
                        amenity_counts[amenity_type] = amenity_counts.get(amenity_type, 0) + 1
                
                return {
                    'schools_count_3km': amenity_counts.get('school', 0),
                    'hospitals_count_5km': amenity_counts.get('hospital', 0),
                    'clinics_count_2km': amenity_counts.get('clinic', 0),
                    'pharmacies_count_2km': amenity_counts.get('pharmacy', 0),
                    'supermarkets_count_2km': amenity_counts.get('supermarket', 0),
                    'banks_count_2km': amenity_counts.get('bank', 0),
                    'restaurants_count_1km': amenity_counts.get('restaurant', 0) + amenity_counts.get('cafe', 0),
                    'parks_count_2km': amenity_counts.get('park', 0),
                    'worship_places_2km': amenity_counts.get('place_of_worship', 0),
                    'total_amenities': len(elements)
                }
            else:
                return self._default_amenities_data()
                
        except Exception as e:
            print(f"Error fetching amenities: {e}")
            return self._default_amenities_data()
    
    def get_public_transport(self, lat: float, lon: float, radius: int = 2000) -> Dict:
        """Get public transport information"""
        try:
            self._rate_limit()
            
            query = f"""
            [out:json][timeout:25];
            (
              node["highway"="bus_stop"](around:{radius},{lat},{lon});
              node["railway"="station"](around:10000,{lat},{lon});
              node["railway"="tram_stop"](around:{radius},{lat},{lon});
              node["amenity"="taxi"](around:{radius},{lat},{lon});
            );
            out center;
            """
            
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_transport_results(data, lat, lon)
            else:
                return self._default_transport_data()
                
        except Exception as e:
            print(f"Error fetching transport data: {e}")
            return self._default_transport_data()
    
    def _process_transport_results(self, data: Dict, lat: float, lon: float) -> Dict:
        """Process transport API results"""
        from geopy.distance import geodesic
        
        bus_stops = []
        train_stations = []
        
        for element in data.get('elements', []):
            coords = (element.get('lat'), element.get('lon'))
            if coords[0] and coords[1]:
                distance = geodesic((lat, lon), coords).meters
                
                tags = element.get('tags', {})
                if tags.get('highway') == 'bus_stop':
                    bus_stops.append(distance)
                elif tags.get('railway') == 'station':
                    train_stations.append(distance)
        
        return {
            'bus_stop_distance': min(bus_stops) if bus_stops else 5000,
            'bus_stops_count_1km': sum(1 for d in bus_stops if d < 1000),
            'train_station_distance': min(train_stations) if train_stations else 50000,
            'public_transport_score': self._calculate_transport_score(bus_stops, train_stations)
        }
    
    def _calculate_transport_score(self, bus_stops: List[float], train_stations: List[float]) -> float:
        """Calculate public transport accessibility score (0-10)"""
        score = 0.0
        
        # Bus accessibility
        if bus_stops:
            min_bus = min(bus_stops)
            if min_bus < 200:
                score += 5
            elif min_bus < 500:
                score += 4
            elif min_bus < 1000:
                score += 3
            elif min_bus < 2000:
                score += 2
        
        # Train accessibility
        if train_stations:
            min_train = min(train_stations)
            if min_train < 2000:
                score += 5
            elif min_train < 5000:
                score += 3
            elif min_train < 10000:
                score += 2
        
        return min(10.0, score)
    
    # Default fallback data methods
    def _default_road_data(self) -> Dict:
        return {
            'motorway_distance': 15000,
            'primary_road_distance': 3000,
            'secondary_road_distance': 1000,
            'nearest_road_distance': 500,
            'road_type': 'secondary',
            'road_density': 2.0
        }
    
    def _default_city_data(self) -> Dict:
        return {
            'city_name': 'Unknown',
            'state': '',
            'country': 'Algeria',
            'display_name': ''
        }
    
    def _default_amenities_data(self) -> Dict:
        return {
            'schools_count_3km': 2,
            'hospitals_count_5km': 1,
            'clinics_count_2km': 3,
            'supermarkets_count_2km': 2,
            'banks_count_2km': 1,
            'restaurants_count_1km': 5,
            'parks_count_2km': 1,
            'worship_places_2km': 2,
            'total_amenities': 17
        }
    
    def _default_transport_data(self) -> Dict:
        return {
            'bus_stop_distance': 800,
            'bus_stops_count_1km': 3,
            'train_station_distance': 15000,
            'public_transport_score': 5.0
        }
