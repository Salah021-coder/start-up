# ============================================================================
# FILE: core/boundary_manager.py (FIXED - EE Optional)
# ============================================================================

import geopandas as gpd
from shapely.geometry import Polygon, shape
import json
from typing import Dict, Optional, Tuple
from utils.geometry_utils import GeometryUtils
from utils.validators import Validators

class BoundaryManager:
    """Handle boundary drawing and import operations"""
    
    def __init__(self):
        self.geometry_utils = GeometryUtils()
        self.validators = Validators()
        self.ee_available = self._check_ee_available()
    
    def _check_ee_available(self) -> bool:
        """Check if Earth Engine is available and initialized"""
        try:
            import ee
            # Try to make a simple call to check if initialized
            ee.String('test').getInfo()
            return True
        except Exception:
            return False
    
    def create_from_coordinates(self, coordinates: list) -> Dict:
        """
        Create boundary from list of coordinates
        Args:
            coordinates: List of [lon, lat] pairs
        Returns:
            Dict with boundary geometry and metadata
        """
        try:
            # Create polygon
            polygon = Polygon(coordinates)
            
            # Validate
            if not self.validators.validate_geometry(polygon):
                raise ValueError("Invalid polygon geometry")
            
            # Calculate area
            area_m2 = self.geometry_utils.calculate_area(polygon)
            area_hectares = area_m2 / 10000
            area_acres = area_hectares * 2.47105
            
            # Create base result
            result = {
                'geometry': polygon,
                'geojson': self._to_geojson(polygon),
                'centroid': list(polygon.centroid.coords[0]),
                'bounds': polygon.bounds,
                'area_m2': area_m2,
                'area_hectares': area_hectares,
                'area_acres': area_acres,
                'perimeter_m': polygon.length * 111320  # Rough conversion
            }
            
            # Only add EE geometry if Earth Engine is available
            if self.ee_available:
                result['ee_geometry'] = self._to_ee_geometry(polygon)
            else:
                result['ee_geometry'] = None
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to create boundary: {str(e)}")
    
    def import_from_file(self, file_path: str, file_type: str) -> Dict:
        """Import boundary from file (KML, GeoJSON, Shapefile)"""
        try:
            if file_type.lower() == 'geojson':
                gdf = gpd.read_file(file_path)
            elif file_type.lower() == 'kml':
                gdf = gpd.read_file(file_path, driver='KML')
            elif file_type.lower() in ['shp', 'shapefile']:
                gdf = gpd.read_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Get the first geometry
            geometry = gdf.geometry.iloc[0]
            
            # Convert to WGS84 if needed
            if gdf.crs and gdf.crs != 'EPSG:4326':
                gdf = gdf.to_crs('EPSG:4326')
                geometry = gdf.geometry.iloc[0]
            
            # Create boundary from geometry
            coordinates = list(geometry.exterior.coords)
            return self.create_from_coordinates(coordinates)
            
        except Exception as e:
            raise ValueError(f"Failed to import file: {str(e)}")
    
    def import_from_geojson_dict(self, geojson: Dict) -> Dict:
        """Import boundary from GeoJSON dictionary"""
        try:
            geometry = shape(geojson['geometry'])
            coordinates = list(geometry.exterior.coords)
            return self.create_from_coordinates(coordinates)
        except Exception as e:
            raise ValueError(f"Failed to import GeoJSON: {str(e)}")
    
    def validate_boundary(self, boundary: Dict) -> Tuple[bool, str]:
        """
        Validate boundary meets requirements
        Returns: (is_valid, message)
        """
        from config.settings import Settings
        
        area_km2 = boundary['area_m2'] / 1_000_000
        
        if area_km2 > Settings.MAX_ANALYSIS_AREA_KM2:
            return False, f"Area too large. Maximum: {Settings.MAX_ANALYSIS_AREA_KM2} km²"
        
        if boundary['area_m2'] < Settings.MIN_ANALYSIS_AREA_M2:
            return False, f"Area too small. Minimum: {Settings.MIN_ANALYSIS_AREA_M2} m²"
        
        if not boundary['geometry'].is_valid:
            return False, "Invalid geometry"
        
        return True, "Boundary is valid"
    
    def _to_geojson(self, geometry) -> Dict:
        """Convert Shapely geometry to GeoJSON"""
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [list(geometry.exterior.coords)]
            },
            'properties': {}
        }
    
    def _to_ee_geometry(self, geometry):
        """Convert Shapely geometry to Earth Engine geometry"""
        try:
            import ee
            coords = list(geometry.exterior.coords)
            return ee.Geometry.Polygon(coords)
        except Exception:
            return None