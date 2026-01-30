# ============================================================================
# FILE: core/boundary_manager.py
# Boundary Processing and Validation
# ============================================================================

import ee
from shapely.geometry import Polygon, shape, mapping
from shapely.ops import transform
import pyproj
import json
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BoundaryManager:
    """
    Manages boundary geometry processing and validation
    
    RESPONSIBILITIES:
    - Convert various input formats to standardized boundary data
    - Validate geometry
    - Calculate area, perimeter, centroid
    - Create Earth Engine geometry for GEE operations
    - Ensure single source of truth for boundary metadata
    """
    
    def __init__(self):
        """Initialize boundary manager"""
        # WGS84 projection (lat/lon)
        self.wgs84 = pyproj.CRS('EPSG:4326')
        
        # UTM projection for accurate area calculations (will be set dynamically)
        self.utm_crs = None
    
    def create_from_coordinates(
        self,
        coordinates: List[List[float]]
    ) -> Dict:
        """
        Create boundary from coordinate list
        
        Args:
            coordinates: List of [lon, lat] pairs
            
        Returns:
            Standardized boundary dict
            
        Raises:
            ValueError: If coordinates invalid
        """
        logger.info(f"Creating boundary from {len(coordinates)} coordinates")
        
        # Validate coordinates
        self._validate_coordinates(coordinates)
        
        # Create Shapely polygon
        # Coordinates are [lon, lat] which is correct for Shapely
        polygon = Polygon(coordinates)
        
        if not polygon.is_valid:
            logger.error("Invalid polygon geometry")
            raise ValueError("Invalid polygon: geometry is not valid")
        
        # Process the polygon
        return self._process_polygon(polygon)
    
    def import_from_geojson_dict(
        self,
        geojson_dict: Dict
    ) -> Dict:
        """
        Import boundary from GeoJSON dictionary
        
        Args:
            geojson_dict: GeoJSON feature or geometry dict
            
        Returns:
            Standardized boundary dict
        """
        logger.info("Importing boundary from GeoJSON")
        
        try:
            # Handle both Feature and Geometry types
            if geojson_dict.get('type') == 'Feature':
                geometry = geojson_dict['geometry']
            elif geojson_dict.get('type') in ['Polygon', 'MultiPolygon']:
                geometry = geojson_dict
            else:
                raise ValueError(f"Unsupported GeoJSON type: {geojson_dict.get('type')}")
            
            # Convert to Shapely geometry
            polygon = shape(geometry)
            
            # Handle MultiPolygon (take largest polygon)
            if polygon.geom_type == 'MultiPolygon':
                logger.warning("MultiPolygon detected, using largest polygon")
                polygon = max(polygon.geoms, key=lambda p: p.area)
            
            if not polygon.is_valid:
                logger.error("Invalid polygon in GeoJSON")
                raise ValueError("Invalid polygon geometry")
            
            return self._process_polygon(polygon)
            
        except Exception as e:
            logger.error(f"Failed to import GeoJSON: {e}")
            raise ValueError(f"Invalid GeoJSON: {str(e)}")
    
    def import_from_shapely(
        self,
        polygon: Polygon
    ) -> Dict:
        """
        Import boundary from Shapely polygon
        
        Args:
            polygon: Shapely Polygon object
            
        Returns:
            Standardized boundary dict
        """
        logger.info("Importing boundary from Shapely polygon")
        
        if not isinstance(polygon, Polygon):
            raise ValueError(f"Expected Polygon, got {type(polygon)}")
        
        if not polygon.is_valid:
            raise ValueError("Invalid polygon geometry")
        
        return self._process_polygon(polygon)
    
    def _process_polygon(
        self,
        polygon: Polygon
    ) -> Dict:
        """
        Process polygon into standardized boundary data
        
        Args:
            polygon: Validated Shapely polygon in WGS84
            
        Returns:
            Complete boundary dict with all metadata
        """
        # Get centroid
        centroid = polygon.centroid
        centroid_coords = [centroid.x, centroid.y]  # [lon, lat]
        
        logger.info(f"Polygon centroid: {centroid_coords[1]:.4f}°N, {centroid_coords[0]:.4f}°E")
        
        # Calculate accurate area using UTM projection
        area_m2, perimeter_m = self._calculate_accurate_metrics(polygon, centroid_coords)
        
        # Convert area to various units
        area_hectares = area_m2 / 10000  # 1 hectare = 10,000 m²
        area_acres = area_m2 / 4046.86  # 1 acre = 4046.86 m²
        area_km2 = area_m2 / 1_000_000
        
        logger.info(f"Area: {area_hectares:.2f} ha ({area_km2:.4f} km²)")
        
        # Validate area
        if area_m2 < 100:
            raise ValueError(f"Area too small: {area_m2:.0f} m² (minimum: 100 m²)")
        
        if area_km2 > 100:
            raise ValueError(f"Area too large: {area_km2:.2f} km² (maximum: 100 km²)")
        
        # Get bounds
        minx, miny, maxx, maxy = polygon.bounds
        
        # Create Earth Engine geometry (if EE available)
        ee_geometry = self._create_ee_geometry(polygon)
        
        # Create GeoJSON representation
        geojson = mapping(polygon)
        
        # Build complete boundary data
        boundary_data = {
            # Core geometry
            'geometry': polygon,  # Shapely polygon
            'geojson': geojson,  # GeoJSON dict
            'ee_geometry': ee_geometry,  # Earth Engine geometry
            
            # Measurements
            'area_m2': area_m2,
            'area_hectares': area_hectares,
            'area_acres': area_acres,
            'area_km2': area_km2,
            'perimeter_m': perimeter_m,
            
            # Location
            'centroid': centroid_coords,  # [lon, lat]
            'bounds': {
                'minx': minx,
                'miny': miny,
                'maxx': maxx,
                'maxy': maxy
            },
            
            # Metadata
            'coordinate_count': len(polygon.exterior.coords),
            'is_valid': polygon.is_valid,
            'utm_zone': self._get_utm_zone(centroid_coords[0], centroid_coords[1])
        }
        
        logger.info("Boundary processing complete")
        
        return boundary_data
    
    def _validate_coordinates(
        self,
        coordinates: List[List[float]]
    ):
        """
        Validate coordinate list
        
        Raises:
            ValueError: If coordinates invalid
        """
        if not coordinates or len(coordinates) < 3:
            raise ValueError(f"At least 3 coordinates required, got {len(coordinates)}")
        
        # Check each coordinate pair
        for i, coord in enumerate(coordinates):
            if len(coord) != 2:
                raise ValueError(f"Coordinate {i} must have 2 values [lon, lat], got {len(coord)}")
            
            lon, lat = coord
            
            # Validate longitude [-180, 180]
            if not (-180 <= lon <= 180):
                raise ValueError(f"Invalid longitude at coordinate {i}: {lon} (must be -180 to 180)")
            
            # Validate latitude [-90, 90]
            if not (-90 <= lat <= 90):
                raise ValueError(f"Invalid latitude at coordinate {i}: {lat} (must be -90 to 90)")
        
        # Check for closed polygon (first == last)
        if coordinates[0] != coordinates[-1]:
            logger.warning("Polygon not closed, automatically closing")
            coordinates.append(coordinates[0])
    
    def _calculate_accurate_metrics(
        self,
        polygon: Polygon,
        centroid: List[float]
    ) -> Tuple[float, float]:
        """
        Calculate area and perimeter using appropriate UTM projection
        
        Args:
            polygon: Polygon in WGS84
            centroid: [lon, lat]
            
        Returns:
            (area_m2, perimeter_m)
        """
        lon, lat = centroid
        
        # Determine UTM zone
        utm_zone = self._get_utm_zone(lon, lat)
        utm_epsg = self._utm_zone_to_epsg(utm_zone, lat >= 0)
        
        logger.debug(f"Using UTM zone {utm_zone} (EPSG:{utm_epsg}) for area calculation")
        
        # Create transformer
        transformer = pyproj.Transformer.from_crs(
            self.wgs84,
            pyproj.CRS(f'EPSG:{utm_epsg}'),
            always_xy=True
        )
        
        # Project polygon to UTM
        polygon_utm = transform(transformer.transform, polygon)
        
        # Calculate metrics in meters
        area_m2 = polygon_utm.area
        perimeter_m = polygon_utm.length
        
        return area_m2, perimeter_m
    
    def _get_utm_zone(self, lon: float, lat: float) -> int:
        """Calculate UTM zone number from longitude"""
        return int((lon + 180) / 6) + 1
    
    def _utm_zone_to_epsg(self, zone: int, northern: bool) -> int:
        """
        Convert UTM zone to EPSG code
        
        Args:
            zone: UTM zone (1-60)
            northern: True if northern hemisphere
            
        Returns:
            EPSG code
        """
        if northern:
            return 32600 + zone  # WGS84 / UTM zone N
        else:
            return 32700 + zone  # WGS84 / UTM zone S
    
    def _create_ee_geometry(
        self,
        polygon: Polygon
    ) -> Optional[ee.Geometry]:
        """
        Create Earth Engine geometry from Shapely polygon
        
        Args:
            polygon: Shapely polygon
            
        Returns:
            ee.Geometry.Polygon or None if EE not available
        """
        try:
            # Test if EE is initialized
            ee.String('test').getInfo()
            
            # Get coordinates (exterior ring only)
            coords = list(polygon.exterior.coords)
            
            # EE expects [lon, lat] pairs (which is what we have)
            ee_coords = [[lon, lat] for lon, lat in coords]
            
            # Create EE geometry
            ee_geom = ee.Geometry.Polygon(ee_coords)
            
            logger.debug("Earth Engine geometry created")
            return ee_geom
            
        except Exception as e:
            logger.warning(f"Earth Engine not available: {e}")
            return None
    
    def validate_boundary(
        self,
        boundary_data: Dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate boundary data structure
        
        Args:
            boundary_data: Boundary dict to validate
            
        Returns:
            (is_valid, error_message)
        """
        required_fields = [
            'geometry', 'geojson', 'area_m2', 'area_hectares',
            'centroid', 'bounds', 'perimeter_m'
        ]
        
        for field in required_fields:
            if field not in boundary_data:
                return False, f"Missing required field: {field}"
        
        # Validate geometry
        if not isinstance(boundary_data['geometry'], Polygon):
            return False, "Invalid geometry type"
        
        if not boundary_data['geometry'].is_valid:
            return False, "Invalid polygon geometry"
        
        # Validate area
        if boundary_data['area_m2'] < 100:
            return False, f"Area too small: {boundary_data['area_m2']:.0f} m²"
        
        if boundary_data['area_km2'] > 100:
            return False, f"Area too large: {boundary_data['area_km2']:.2f} km²"
        
        return True, None
    
    def get_boundary_summary(
        self,
        boundary_data: Dict
    ) -> str:
        """
        Get human-readable boundary summary
        
        Args:
            boundary_data: Boundary dict
            
        Returns:
            Summary string
        """
        return f"""
Boundary Summary:
- Area: {boundary_data['area_hectares']:.2f} hectares ({boundary_data['area_acres']:.2f} acres)
- Perimeter: {boundary_data['perimeter_m']:.0f} meters
- Centroid: {boundary_data['centroid'][1]:.4f}°N, {boundary_data['centroid'][0]:.4f}°E
- Coordinates: {boundary_data['coordinate_count']} points
- UTM Zone: {boundary_data['utm_zone']}
""".strip()
