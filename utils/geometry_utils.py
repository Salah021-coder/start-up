from shapely.geometry import Polygon, Point
import math

class GeometryUtils:
    """Utility functions for geometry operations"""
    
    @staticmethod
    def calculate_area(polygon: Polygon) -> float:
        """
        Calculate area in square meters
        Using approximate conversion for lat/lon to meters
        """
        # This is a simplified calculation
        # For production, use proper projection
        
        bounds = polygon.bounds
        # Approximate meters per degree at given latitude
        lat_mid = (bounds[1] + bounds[3]) / 2
        meters_per_deg_lat = 111320  # roughly constant
        meters_per_deg_lon = 111320 * math.cos(math.radians(lat_mid))
        
        # Get area in square degrees
        area_deg = polygon.area
        
        # Convert to square meters
        area_m2 = area_deg * meters_per_deg_lat * meters_per_deg_lon
        
        return area_m2
    
    @staticmethod
    def calculate_perimeter(polygon: Polygon) -> float:
        """Calculate perimeter in meters"""
        return polygon.length * 111320  # Rough conversion
    
    @staticmethod
    def get_centroid(polygon: Polygon) -> tuple:
        """Get centroid coordinates"""
        centroid = polygon.centroid
        return (centroid.x, centroid.y)
