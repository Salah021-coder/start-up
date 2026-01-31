# ============================================================================
# FILE: utils/coordinate_utils.py
# Coordinate System Utilities
# ============================================================================

import math
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class CoordinateUtils:
    """Coordinate system conversions and calculations"""
    
    # Earth radius in meters
    EARTH_RADIUS_M = 6371000
    
    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        Args:
            lat1: Latitude of point 1 (degrees)
            lon1: Longitude of point 1 (degrees)
            lat2: Latitude of point 2 (degrees)
            lon2: Longitude of point 2 (degrees)
            
        Returns:
            Distance in meters
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon / 2) ** 2
        
        c = 2 * math.asin(math.sqrt(a))
        
        return CoordinateUtils.EARTH_RADIUS_M * c
    
    @staticmethod
    def degrees_to_meters(
        degrees: float,
        latitude: float
    ) -> float:
        """
        Convert degrees to meters at given latitude
        
        Args:
            degrees: Distance in degrees
            latitude: Latitude (degrees)
            
        Returns:
            Distance in meters
        """
        # Meters per degree longitude varies with latitude
        meters_per_deg_lat = 111320  # roughly constant
        meters_per_deg_lon = 111320 * math.cos(math.radians(latitude))
        
        # Use average for rough conversion
        avg_meters_per_deg = (meters_per_deg_lat + meters_per_deg_lon) / 2
        
        return degrees * avg_meters_per_deg
    
    @staticmethod
    def meters_to_degrees(
        meters: float,
        latitude: float
    ) -> float:
        """
        Convert meters to degrees at given latitude
        
        Args:
            meters: Distance in meters
            latitude: Latitude (degrees)
            
        Returns:
            Distance in degrees
        """
        meters_per_deg = 111320 * math.cos(math.radians(latitude))
        return meters / meters_per_deg
    
    @staticmethod
    def calculate_bbox(
        center_lat: float,
        center_lon: float,
        radius_meters: float
    ) -> Tuple[float, float, float, float]:
        """
        Calculate bounding box around point
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_meters: Radius in meters
            
        Returns:
            (south, west, north, east) in degrees
        """
        # Degrees per meter at this latitude
        meters_per_deg_lat = 111320
        meters_per_deg_lon = 111320 * math.cos(math.radians(center_lat))
        
        delta_lat = radius_meters / meters_per_deg_lat
        delta_lon = radius_meters / meters_per_deg_lon
        
        south = center_lat - delta_lat
        north = center_lat + delta_lat
        west = center_lon - delta_lon
        east = center_lon + delta_lon
        
        return (south, west, north, east)
    
    @staticmethod
    def point_in_bbox(
        lat: float,
        lon: float,
        bbox: Tuple[float, float, float, float]
    ) -> bool:
        """
        Check if point is within bounding box
        
        Args:
            lat: Point latitude
            lon: Point longitude
            bbox: (south, west, north, east)
            
        Returns:
            True if point is in bbox
        """
        south, west, north, east = bbox
        return south <= lat <= north and west <= lon <= east
    
    @staticmethod
    def get_utm_zone(lon: float, lat: float) -> int:
        """
        Get UTM zone number for coordinates
        
        Args:
            lon: Longitude
            lat: Latitude
            
        Returns:
            UTM zone number (1-60)
        """
        # UTM zone formula
        zone = int((lon + 180) / 6) + 1
        
        # Special zones for Norway and Svalbard
        if 56 <= lat < 64 and 3 <= lon < 12:
            zone = 32
        elif 72 <= lat < 84:
            if 0 <= lon < 9:
                zone = 31
            elif 9 <= lon < 21:
                zone = 33
            elif 21 <= lon < 33:
                zone = 35
            elif 33 <= lon < 42:
                zone = 37
        
        return zone
    
    @staticmethod
    def get_utm_epsg(lon: float, lat: float) -> int:
        """
        Get EPSG code for UTM zone
        
        Args:
            lon: Longitude
            lat: Latitude
            
        Returns:
            EPSG code
        """
        zone = CoordinateUtils.get_utm_zone(lon, lat)
        
        # Northern hemisphere: 326XX
        # Southern hemisphere: 327XX
        if lat >= 0:
            epsg = 32600 + zone
        else:
            epsg = 32700 + zone
        
        return epsg
    
    @staticmethod
    def bearing_between_points(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate bearing from point 1 to point 2
        
        Args:
            lat1: Start latitude
            lon1: Start longitude
            lat2: End latitude
            lon2: End longitude
            
        Returns:
            Bearing in degrees (0-360)
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
            math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        
        bearing_rad = math.atan2(x, y)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalize to 0-360
        return (bearing_deg + 360) % 360
