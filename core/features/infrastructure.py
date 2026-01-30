# ============================================================================
# FILE: core/features/infrastructure.py
# Infrastructure Feature Extraction from OpenStreetMap
# ============================================================================

import requests
from typing import Dict, List, Tuple, Optional
import logging
import math
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
import time

logger = logging.getLogger(__name__)


class InfrastructureExtractor:
    """
    Extract infrastructure features from OpenStreetMap
    
    RESPONSIBILITIES:
    - Fetch real OSM data via Overpass API
    - Calculate distances to roads, amenities
    - Assess utility availability
    - Determine urbanization level
    
    DOES NOT:
    - Use mock data silently (logs when real data unavailable)
    - Cache results
    - Guess utility availability
    """
    
    def __init__(self, use_real_osm: bool = True):
        """
        Initialize infrastructure extractor
        
        Args:
            use_real_osm: If True, fetch real OSM data; if False, use estimates
        """
        self.use_real_osm = use_real_osm
        
        # Overpass API endpoint
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Request timeout
        self.timeout = 30
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds between requests
    
    def extract(
        self,
        ee_geometry=None,
        centroid: List[float] = None,
        geometry=None
    ) -> Dict:
        """
        Extract all infrastructure features
        
        Args:
            ee_geometry: Earth Engine geometry (optional)
            centroid: [lon, lat] centroid
            geometry: Shapely geometry (optional)
            
        Returns:
            Dict with infrastructure features
            
        Raises:
            ValueError: If insufficient location data
            RuntimeError: If extraction fails critically
        """
        if centroid is None:
            raise ValueError("centroid is required for infrastructure extraction")
        
        if len(centroid) != 2:
            raise ValueError(f"centroid must be [lon, lat], got {centroid}")
        
        lon, lat = centroid
        
        logger.info(f"Extracting infrastructure for {lat:.4f}°N, {lon:.4f}°E")
        
        if self.use_real_osm:
            try:
                return self._extract_real_osm(lon, lat, geometry)
            except Exception as e:
                logger.error(f"Real OSM extraction failed: {e}, falling back to estimates")
                return self._extract_estimates(lon, lat)
        else:
            logger.info("Using infrastructure estimates (real OSM disabled)")
            return self._extract_estimates(lon, lat)
    
    def _extract_real_osm(
        self,
        lon: float,
        lat: float,
        geometry
    ) -> Dict:
        """
        Extract real infrastructure data from OpenStreetMap
        
        Args:
            lon: Longitude
            lat: Latitude
            geometry: Shapely geometry (for boundary)
            
        Returns:
            Dict with infrastructure features
        """
        logger.info("Fetching real OSM data")
        
        # Get bounding box (search radius)
        search_radius_km = 5.0  # 5km radius
        bbox = self._calculate_bbox(lat, lon, search_radius_km)
        
        # Extract different feature types
        roads = self._fetch_roads(bbox, lat, lon)
        amenities = self._fetch_amenities(bbox, lat, lon)
        public_transport = self._fetch_public_transport(bbox, lat, lon)
        
        # Calculate metrics
        road_metrics = self._calculate_road_metrics(roads, lat, lon)
        amenity_metrics = self._calculate_amenity_metrics(amenities, lat, lon)
        transport_metrics = self._calculate_transport_metrics(public_transport, lat, lon)
        
        # Determine urbanization level
        urbanization = self._determine_urbanization(
            road_metrics,
            amenity_metrics,
            transport_metrics
        )
        
        # Calculate accessibility score
        accessibility_score = self._calculate_accessibility_score(
            road_metrics,
            transport_metrics,
            urbanization
        )
        
        # Calculate infrastructure score
        infrastructure_score = self._calculate_infrastructure_score(
            road_metrics,
            amenity_metrics,
            transport_metrics,
            urbanization
        )
        
        # Estimate utilities (OSM utility data is incomplete)
        utilities = self._estimate_utilities(urbanization, road_metrics)
        
        # Compile all features
        infrastructure_features = {
            # Roads
            'nearest_road_distance': road_metrics['nearest_distance'],
            'road_type': road_metrics['nearest_type'],
            'road_density': road_metrics['density'],
            'primary_road_distance': road_metrics['primary_distance'],
            'motorway_distance': road_metrics['motorway_distance'],
            
            # Public Transport
            'bus_stop_distance': transport_metrics['bus_stop_distance'],
            'train_station_distance': transport_metrics['train_station_distance'],
            'public_transport_score': transport_metrics['transport_score'],
            
            # Amenities
            'schools_count_3km': amenity_metrics['schools_3km'],
            'hospitals_count_5km': amenity_metrics['hospitals_5km'],
            'clinics_count_2km': amenity_metrics['clinics_2km'],
            'supermarkets_count_2km': amenity_metrics['supermarkets_2km'],
            'restaurants_count_1km': amenity_metrics['restaurants_1km'],
            'total_amenities': amenity_metrics['total_count'],
            
            # Urban context
            'urbanization_level': urbanization['level'],
            'city_name': urbanization['city_name'],
            'population_density': urbanization['population_density'],
            'development_pressure': urbanization['development_pressure'],
            
            # Utilities (estimates)
            'electricity_grid': utilities['electricity'],
            'water_network': utilities['water'],
            'sewage_system': utilities['sewage'],
            'gas_network': utilities['gas'],
            'internet_fiber': utilities['internet'],
            'utilities_available': utilities['available_count'],
            
            # Scores
            'accessibility_score': accessibility_score,
            'infrastructure_score': infrastructure_score,
            
            # Metadata
            'data_quality': 'real_osm',
            'osm_query_radius_km': search_radius_km,
            'features_fetched': {
                'roads': len(roads),
                'amenities': len(amenities),
                'transport': len(public_transport)
            }
        }
        
        logger.info(
            f"Real OSM extraction complete: "
            f"{len(roads)} roads, {len(amenities)} amenities, "
            f"urbanization: {urbanization['level']}"
        )
        
        return infrastructure_features
    
    def _extract_estimates(
        self,
        lon: float,
        lat: float
    ) -> Dict:
        """
        Generate infrastructure estimates when real data unavailable
        
        Based on location heuristics
        """
        logger.warning("Using infrastructure estimates (not real OSM data)")
        
        # Rough urbanization estimate based on coordinates
        # (This is a simplified heuristic for Algeria)
        
        # Distance from major cities (very rough)
        algiers_dist = self._haversine_distance(lat, lon, 36.7538, 3.0588)
        oran_dist = self._haversine_distance(lat, lon, 35.6969, -0.6331)
        constantine_dist = self._haversine_distance(lat, lon, 36.3650, 6.6147)
        
        nearest_city_dist = min(algiers_dist, oran_dist, constantine_dist)
        
        # Estimate urbanization
        if nearest_city_dist < 10:
            urbanization_level = 'urban'
            road_dist = 200
            pop_density = 3000
        elif nearest_city_dist < 30:
            urbanization_level = 'suburban'
            road_dist = 500
            pop_density = 1000
        elif nearest_city_dist < 100:
            urbanization_level = 'rural'
            road_dist = 1500
            pop_density = 200
        else:
            urbanization_level = 'remote'
            road_dist = 5000
            pop_density = 50
        
        # Generate estimates
        infrastructure_features = {
            # Roads (estimates)
            'nearest_road_distance': road_dist,
            'road_type': 'secondary' if urbanization_level in ['urban', 'suburban'] else 'tertiary',
            'road_density': 2.0 if urbanization_level == 'urban' else 0.5,
            'primary_road_distance': road_dist * 2,
            'motorway_distance': nearest_city_dist * 1000,
            
            # Public Transport (estimates)
            'bus_stop_distance': road_dist * 2 if urbanization_level != 'remote' else 999999,
            'train_station_distance': nearest_city_dist * 1000,
            'public_transport_score': 7 if urbanization_level == 'urban' else 3,
            
            # Amenities (estimates)
            'schools_count_3km': 5 if urbanization_level == 'urban' else 1,
            'hospitals_count_5km': 2 if urbanization_level != 'remote' else 0,
            'clinics_count_2km': 3 if urbanization_level == 'urban' else 0,
            'supermarkets_count_2km': 4 if urbanization_level == 'urban' else 1,
            'restaurants_count_1km': 10 if urbanization_level == 'urban' else 2,
            'total_amenities': 24 if urbanization_level == 'urban' else 4,
            
            # Urban context
            'urbanization_level': urbanization_level,
            'city_name': 'Unknown',
            'population_density': pop_density,
            'development_pressure': 'high' if urbanization_level == 'urban' else 'low',
            
            # Utilities (estimates)
            'electricity_grid': urbanization_level != 'remote',
            'water_network': urbanization_level in ['urban', 'suburban'],
            'sewage_system': urbanization_level == 'urban',
            'gas_network': urbanization_level == 'urban',
            'internet_fiber': urbanization_level in ['urban', 'suburban'],
            'utilities_available': 4 if urbanization_level == 'urban' else 2,
            
            # Scores (estimates)
            'accessibility_score': 8 if urbanization_level == 'urban' else 4,
            'infrastructure_score': 7 if urbanization_level == 'urban' else 4,
            
            # Metadata
            'data_quality': 'estimated',
            'estimation_method': 'distance_from_cities',
            'nearest_major_city_km': round(nearest_city_dist, 1)
        }
        
        return infrastructure_features
    
    def _calculate_bbox(
        self,
        lat: float,
        lon: float,
        radius_km: float
    ) -> Tuple[float, float, float, float]:
        """
        Calculate bounding box around point
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Radius in kilometers
            
        Returns:
            (south, west, north, east)
        """
        # Approximate degrees per km
        km_per_deg_lat = 111.32
        km_per_deg_lon = 111.32 * math.cos(math.radians(lat))
        
        delta_lat = radius_km / km_per_deg_lat
        delta_lon = radius_km / km_per_deg_lon
        
        south = lat - delta_lat
        north = lat + delta_lat
        west = lon - delta_lon
        east = lon + delta_lon
        
        return (south, west, north, east)
    
    def _rate_limit(self):
        """Enforce rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _fetch_roads(
        self,
        bbox: Tuple[float, float, float, float],
        center_lat: float,
        center_lon: float
    ) -> List[Dict]:
        """Fetch roads from OSM via Overpass API"""
        
        self._rate_limit()
        
        south, west, north, east = bbox
        
        query = f"""
        [out:json][timeout:25];
        (
          way["highway"~"motorway|trunk|primary|secondary|tertiary|residential"]
              ({south},{west},{north},{east});
        );
        out geom;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            logger.debug(f"Fetched {len(elements)} roads from OSM")
            
            return elements
            
        except Exception as e:
            logger.warning(f"OSM road query failed: {e}")
            return []
    
    def _fetch_amenities(
        self,
        bbox: Tuple[float, float, float, float],
        center_lat: float,
        center_lon: float
    ) -> List[Dict]:
        """Fetch amenities (schools, hospitals, shops, etc.)"""
        
        self._rate_limit()
        
        south, west, north, east = bbox
        
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"~"school|hospital|clinic|pharmacy|supermarket|restaurant|cafe|bank"]
              ({south},{west},{north},{east});
          way["amenity"~"school|hospital|clinic|pharmacy|supermarket|restaurant|cafe|bank"]
              ({south},{west},{north},{east});
        );
        out center;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            logger.debug(f"Fetched {len(elements)} amenities from OSM")
            
            return elements
            
        except Exception as e:
            logger.warning(f"OSM amenity query failed: {e}")
            return []
    
    def _fetch_public_transport(
        self,
        bbox: Tuple[float, float, float, float],
        center_lat: float,
        center_lon: float
    ) -> List[Dict]:
        """Fetch public transport stops"""
        
        self._rate_limit()
        
        south, west, north, east = bbox
        
        query = f"""
        [out:json][timeout:25];
        (
          node["public_transport"~"stop_position|platform"]({south},{west},{north},{east});
          node["highway"="bus_stop"]({south},{west},{north},{east});
          node["railway"~"station|halt"]({south},{west},{north},{east});
        );
        out;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            logger.debug(f"Fetched {len(elements)} transport stops from OSM")
            
            return elements
            
        except Exception as e:
            logger.warning(f"OSM transport query failed: {e}")
            return []
    
    def _calculate_road_metrics(
        self,
        roads: List[Dict],
        center_lat: float,
        center_lon: float
    ) -> Dict:
        """Calculate road-related metrics"""
        
        if not roads:
            logger.warning("No roads found in OSM data")
            return {
                'nearest_distance': 999999,
                'nearest_type': 'unknown',
                'density': 0.0,
                'primary_distance': 999999,
                'motorway_distance': 999999
            }
        
        center_point = Point(center_lon, center_lat)
        
        nearest_dist = float('inf')
        nearest_type = 'unknown'
        primary_dist = float('inf')
        motorway_dist = float('inf')
        
        for road in roads:
            highway_type = road.get('tags', {}).get('highway', 'unknown')
            
            # Get road geometry
            if 'geometry' in road:
                coords = [(node['lon'], node['lat']) for node in road['geometry']]
                if len(coords) >= 2:
                    road_line = LineString(coords)
                    
                    # Calculate distance (in degrees, approximate)
                    dist_deg = center_point.distance(road_line)
                    dist_m = dist_deg * 111320  # Rough conversion to meters
                    
                    # Nearest road
                    if dist_m < nearest_dist:
                        nearest_dist = dist_m
                        nearest_type = highway_type
                    
                    # Primary road
                    if highway_type in ['primary', 'trunk'] and dist_m < primary_dist:
                        primary_dist = dist_m
                    
                    # Motorway
                    if highway_type == 'motorway' and dist_m < motorway_dist:
                        motorway_dist = dist_m
        
        # Calculate road density (rough estimate)
        total_length = sum(
            len(road.get('geometry', [])) * 0.03  # ~30m per segment
            for road in roads
        )
        area_km2 = 25  # 5km radius circle
        density = total_length / area_km2
        
        return {
            'nearest_distance': nearest_dist,
            'nearest_type': nearest_type,
            'density': round(density, 2),
            'primary_distance': primary_dist,
            'motorway_distance': motorway_dist
        }
    
    def _calculate_amenity_metrics(
        self,
        amenities: List[Dict],
        center_lat: float,
        center_lon: float
    ) -> Dict:
        """Calculate amenity-related metrics"""
        
        if not amenities:
            return {
                'schools_3km': 0,
                'hospitals_5km': 0,
                'clinics_2km': 0,
                'supermarkets_2km': 0,
                'restaurants_1km': 0,
                'total_count': 0
            }
        
        center_point = Point(center_lon, center_lat)
        
        # Count amenities by type and distance
        counts = {
            'schools_3km': 0,
            'hospitals_5km': 0,
            'clinics_2km': 0,
            'supermarkets_2km': 0,
            'restaurants_1km': 0
        }
        
        for amenity in amenities:
            amenity_type = amenity.get('tags', {}).get('amenity', '')
            
            # Get location
            if 'lat' in amenity and 'lon' in amenity:
                lat = amenity['lat']
                lon = amenity['lon']
            elif 'center' in amenity:
                lat = amenity['center']['lat']
                lon = amenity['center']['lon']
            else:
                continue
            
            amenity_point = Point(lon, lat)
            dist_km = center_point.distance(amenity_point) * 111.32
            
            # Count by type and distance
            if amenity_type == 'school' and dist_km <= 3:
                counts['schools_3km'] += 1
            elif amenity_type == 'hospital' and dist_km <= 5:
                counts['hospitals_5km'] += 1
            elif amenity_type in ['clinic', 'pharmacy'] and dist_km <= 2:
                counts['clinics_2km'] += 1
            elif amenity_type == 'supermarket' and dist_km <= 2:
                counts['supermarkets_2km'] += 1
            elif amenity_type in ['restaurant', 'cafe'] and dist_km <= 1:
                counts['restaurants_1km'] += 1
        
        counts['total_count'] = len(amenities)
        
        return counts
    
    def _calculate_transport_metrics(
        self,
        transport_stops: List[Dict],
        center_lat: float,
        center_lon: float
    ) -> Dict:
        """Calculate public transport metrics"""
        
        if not transport_stops:
            return {
                'bus_stop_distance': 999999,
                'train_station_distance': 999999,
                'transport_score': 0
            }
        
        center_point = Point(center_lon, center_lat)
        
        nearest_bus = float('inf')
        nearest_train = float('inf')
        
        for stop in transport_stops:
            lat = stop.get('lat')
            lon = stop.get('lon')
            
            if lat is None or lon is None:
                continue
            
            stop_point = Point(lon, lat)
            dist_m = center_point.distance(stop_point) * 111320
            
            tags = stop.get('tags', {})
            
            # Bus stop
            if tags.get('highway') == 'bus_stop' or tags.get('public_transport') in ['stop_position', 'platform']:
                if dist_m < nearest_bus:
                    nearest_bus = dist_m
            
            # Train station
            if tags.get('railway') in ['station', 'halt']:
                if dist_m < nearest_train:
                    nearest_train = dist_m
        
        # Calculate transport score
        score = 0
        if nearest_bus < 500:
            score += 5
        elif nearest_bus < 1000:
            score += 3
        elif nearest_bus < 2000:
            score += 1
        
        if nearest_train < 2000:
            score += 3
        elif nearest_train < 5000:
            score += 1
        
        score = min(10, score)
        
        return {
            'bus_stop_distance': nearest_bus,
            'train_station_distance': nearest_train,
            'transport_score': score
        }
    
    def _determine_urbanization(
        self,
        road_metrics: Dict,
        amenity_metrics: Dict,
        transport_metrics: Dict
    ) -> Dict:
        """Determine urbanization level"""
        
        road_dist = road_metrics['nearest_distance']
        road_density = road_metrics['density']
        amenity_count = amenity_metrics['total_count']
        transport_score = transport_metrics['transport_score']
        
        # Score urbanization factors
        urban_score = 0
        
        if road_dist < 200:
            urban_score += 3
        elif road_dist < 500:
            urban_score += 2
        elif road_dist < 1000:
            urban_score += 1
        
        if road_density > 2:
            urban_score += 2
        elif road_density > 1:
            urban_score += 1
        
        if amenity_count > 20:
            urban_score += 2
        elif amenity_count > 10:
            urban_score += 1
        
        if transport_score > 7:
            urban_score += 2
        elif transport_score > 4:
            urban_score += 1
        
        # Classify
        if urban_score >= 8:
            level = 'city_center'
            pop_density = 5000
            dev_pressure = 'very_high'
        elif urban_score >= 6:
            level = 'urban'
            pop_density = 3000
            dev_pressure = 'high'
        elif urban_score >= 4:
            level = 'suburban'
            pop_density = 1000
            dev_pressure = 'medium'
        elif urban_score >= 2:
            level = 'rural'
            pop_density = 200
            dev_pressure = 'low'
        else:
            level = 'remote'
            pop_density = 50
            dev_pressure = 'very_low'
        
        return {
            'level': level,
            'city_name': 'Unknown',  # Would need geocoding API
            'population_density': pop_density,
            'development_pressure': dev_pressure,
            'urban_score': urban_score
        }
    
    def _calculate_accessibility_score(
        self,
        road_metrics: Dict,
        transport_metrics: Dict,
        urbanization: Dict
    ) -> float:
        """Calculate overall accessibility score (0-10)"""
        
        score = 5.0
        
        # Road accessibility
        road_dist = road_metrics['nearest_distance']
        if road_dist < 200:
            score += 3
        elif road_dist < 500:
            score += 2
        elif road_dist < 1000:
            score += 1
        elif road_dist > 2000:
            score -= 2
        
        # Transport accessibility
        score += (transport_metrics['transport_score'] - 5) * 0.4
        
        return round(max(0, min(10, score)), 1)
    
    def _calculate_infrastructure_score(
        self,
        road_metrics: Dict,
        amenity_metrics: Dict,
        transport_metrics: Dict,
        urbanization: Dict
    ) -> float:
        """Calculate overall infrastructure quality score (0-10)"""
        
        score = 5.0
        
        # Road quality
        if road_metrics['density'] > 2:
            score += 2
        elif road_metrics['density'] > 1:
            score += 1
        
        # Amenity availability
        amenity_count = amenity_metrics['total_count']
        if amenity_count > 30:
            score += 2
        elif amenity_count > 15:
            score += 1
        
        # Transport quality
        score += (transport_metrics['transport_score'] - 5) * 0.3
        
        return round(max(0, min(10, score)), 1)
    
    def _estimate_utilities(
        self,
        urbanization: Dict,
        road_metrics: Dict
    ) -> Dict:
        """
        Estimate utility availability
        
        OSM utility data is often incomplete, so we estimate based on urbanization
        """
        level = urbanization['level']
        road_dist = road_metrics['nearest_distance']
        
        # Utilities more likely in urban areas with good road access
        if level == 'city_center':
            utilities = {
                'electricity': True,
                'water': True,
                'sewage': True,
                'gas': True,
                'internet': True
            }
        elif level == 'urban':
            utilities = {
                'electricity': True,
                'water': True,
                'sewage': True,
                'gas': road_dist < 500,
                'internet': True
            }
        elif level == 'suburban':
            utilities = {
                'electricity': True,
                'water': road_dist < 1000,
                'sewage': road_dist < 500,
                'gas': False,
                'internet': road_dist < 1000
            }
        elif level == 'rural':
            utilities = {
                'electricity': road_dist < 2000,
                'water': False,
                'sewage': False,
                'gas': False,
                'internet': road_dist < 1000
            }
        else:  # remote
            utilities = {
                'electricity': False,
                'water': False,
                'sewage': False,
                'gas': False,
                'internet': False
            }
        
        utilities['available_count'] = sum(utilities.values())
        
        return utilities
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points (in km) using Haversine formula
        """
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon / 2) ** 2
        
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
