from shapely.geometry import Polygon

class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_geometry(polygon: Polygon) -> bool:
        """Validate polygon geometry"""
        if not polygon.is_valid:
            return False
        
        if polygon.is_empty:
            return False
        
        if not polygon.exterior:
            return False
        
        # Check for minimum number of points
        if len(polygon.exterior.coords) < 4:
            return False
        
        return True
    
    @staticmethod
    def validate_coordinates(coords: list) -> bool:
        """Validate coordinate list"""
        if not coords or len(coords) < 3:
            return False
        
        # Check each coordinate pair
        for coord in coords:
            if len(coord) != 2:
                return False
            
            lon, lat = coord
            
            # Validate longitude [-180, 180]
            if lon < -180 or lon > 180:
                return False
            
            # Validate latitude [-90, 90]
            if lat < -90 or lat > 90:
                return False
        
        return True
