# ============================================================================
# FILE: intelligence/spatial/suitability_grid.py (NEW FILE)
# ============================================================================

import ee
import numpy as np
from typing import Dict, List, Tuple
from shapely.geometry import box, Point
import json

class SuitabilityGridAnalyzer:
    """
    Analyze suitability across a grid of points within a boundary
    Creates heatmap showing best locations for specific land uses
    """
    
    def __init__(self, grid_size_meters: int = 100):
        """
        Args:
            grid_size_meters: Size of each grid cell in meters (default 100m)
        """
        self.grid_size = grid_size_meters
        self.grid_size_degrees = grid_size_meters / 111320  # Approximate conversion
    
    def analyze_area(
        self,
        boundary_geometry,  # Shapely geometry
        land_use_type: str = 'residential',
        max_points: int = 100
    ) -> Dict:
        """
        Analyze suitability across the entire area
        
        Args:
            boundary_geometry: Shapely polygon of the area
            land_use_type: Type of land use to optimize for
            max_points: Maximum number of grid points to analyze
            
        Returns:
            Dict with grid analysis results and heatmap data
        """
        
        print(f"\n=== Starting Grid Suitability Analysis ===")
        print(f"Land Use: {land_use_type}")
        print(f"Grid Size: {self.grid_size}m")
        
        # Step 1: Create grid points
        grid_points = self._create_grid_points(boundary_geometry, max_points)
        print(f"Created grid: {len(grid_points)} points")
        
        # Step 2: Analyze each point
        print("Analyzing grid points...")
        analyzed_points = self._analyze_grid_points(
            grid_points,
            boundary_geometry,
            land_use_type
        )
        
        # Step 3: Find best locations
        best_locations = self._find_best_locations(analyzed_points, top_n=5)
        
        # Step 4: Create heatmap data
        heatmap_data = self._create_heatmap_data(analyzed_points)
        
        # Step 5: Generate recommendations
        recommendations = self._generate_location_recommendations(
            best_locations,
            land_use_type
        )
        
        print(f"=== Analysis Complete ===\n")
        
        return {
            'grid_points': analyzed_points,
            'best_locations': best_locations,
            'heatmap_data': heatmap_data,
            'recommendations': recommendations,
            'statistics': self._calculate_statistics(analyzed_points),
            'land_use_type': land_use_type
        }
    
    def _create_grid_points(
        self,
        boundary_geometry,
        max_points: int
    ) -> List[Dict]:
        """Create grid of points within the boundary"""
        
        # Get bounding box
        minx, miny, maxx, maxy = boundary_geometry.bounds
        
        # Calculate grid dimensions
        width = maxx - minx
        height = maxy - miny
        
        # Calculate number of points in each direction
        cols = int(width / self.grid_size_degrees)
        rows = int(height / self.grid_size_degrees)
        
        # Limit total points
        total_points = cols * rows
        if total_points > max_points:
            # Reduce resolution
            scale_factor = np.sqrt(max_points / total_points)
            cols = int(cols * scale_factor)
            rows = int(rows * scale_factor)
            
            # Recalculate grid size
            actual_grid_size_lon = width / cols
            actual_grid_size_lat = height / rows
        else:
            actual_grid_size_lon = self.grid_size_degrees
            actual_grid_size_lat = self.grid_size_degrees
        
        # Create grid points
        grid_points = []
        point_id = 0
        
        for i in range(rows):
            for j in range(cols):
                lon = minx + (j + 0.5) * actual_grid_size_lon
                lat = miny + (i + 0.5) * actual_grid_size_lat
                
                point = Point(lon, lat)
                
                # Only include points inside boundary
                if boundary_geometry.contains(point):
                    grid_points.append({
                        'id': point_id,
                        'lon': lon,
                        'lat': lat,
                        'row': i,
                        'col': j,
                        'geometry': point
                    })
                    point_id += 1
        
        return grid_points
    
    def _analyze_grid_points(
        self,
        grid_points: List[Dict],
        boundary_geometry,
        land_use_type: str
    ) -> List[Dict]:
        """Analyze suitability for each grid point"""
        
        from utils.ee_manager import EarthEngineManager
        
        analyzed = []
        total = len(grid_points)
        
        for idx, point in enumerate(grid_points):
            if idx % 10 == 0:
                print(f"  Progress: {idx}/{total} points...")
            
            # Get features for this point
            features = self._extract_point_features(point, boundary_geometry)
            
            # Calculate suitability score
            suitability = self._calculate_point_suitability(
                features,
                land_use_type
            )
            
            analyzed.append({
                **point,
                'features': features,
                'suitability_score': suitability['score'],
                'category': suitability['category'],
                'reasons': suitability['reasons']
            })
        
        return analyzed
    
    def _extract_point_features(
        self,
        point: Dict,
        boundary_geometry
    ) -> Dict:
        """Extract features for a specific point"""
        
        from utils.ee_manager import EarthEngineManager
        
        lon, lat = point['lon'], point['lat']
        
        # Initialize features
        features = {
            'location': {'lon': lon, 'lat': lat}
        }
        
        # Try to get Earth Engine data
        if EarthEngineManager.is_available():
            try:
                ee_point = ee.Geometry.Point([lon, lat])
                
                # Get elevation and slope
                srtm = ee.Image('USGS/SRTMGL1_003')
                elevation = srtm.sample(ee_point, 30).first().get('elevation').getInfo()
                
                slope_img = ee.Terrain.slope(srtm)
                slope = slope_img.sample(ee_point, 30).first().get('slope').getInfo()
                
                # Get NDVI
                sentinel = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filterDate('2023-01-01', '2023-12-31') \
                    .filterBounds(ee_point) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                    .first()
                
                if sentinel:
                    ndvi = sentinel.normalizedDifference(['B8', 'B4']).sample(ee_point, 30).first()
                    ndvi_value = ndvi.get('nd').getInfo() if ndvi else 0.5
                else:
                    ndvi_value = 0.5
                
                features['terrain'] = {
                    'elevation': elevation or 100,
                    'slope': slope or 5
                }
                
                features['environmental'] = {
                    'ndvi': ndvi_value
                }
                
            except Exception as e:
                # Use defaults if EE fails
                features['terrain'] = {'elevation': 100, 'slope': 5}
                features['environmental'] = {'ndvi': 0.5}
        else:
            # Use estimated values based on position
            features['terrain'] = {'elevation': 100, 'slope': 5}
            features['environmental'] = {'ndvi': 0.5}
        
        # Calculate distance to boundary edges (proximity to access)
        from shapely.geometry import Point as ShapelyPoint
        point_geom = ShapelyPoint(lon, lat)
        distance_to_edge = point_geom.distance(boundary_geometry.exterior) * 111320  # Convert to meters
        
        features['accessibility'] = {
            'distance_to_boundary_edge': distance_to_edge
        }
        
        return features
    
    def _calculate_point_suitability(
        self,
        features: Dict,
        land_use_type: str
    ) -> Dict:
        """Calculate suitability score for a point"""
        
        score = 5.0  # Base score
        reasons = []
        
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        access = features.get('accessibility', {})
        
        slope = terrain.get('slope', 5)
        elevation = terrain.get('elevation', 100)
        ndvi = env.get('ndvi', 0.5)
        edge_distance = access.get('distance_to_boundary_edge', 0)
        
        # === Land Use Specific Scoring ===
        
        if land_use_type in ['residential', 'commercial']:
            # Prefer flatter areas
            if slope < 3:
                score += 3.0
                reasons.append("Very flat - ideal for construction")
            elif slope < 8:
                score += 1.5
                reasons.append("Gentle slope - suitable for building")
            elif slope > 15:
                score -= 2.0
                reasons.append("Steep slope - challenging terrain")
            
            # Prefer accessible locations (near edges/roads)
            if edge_distance < 50:
                score += 2.0
                reasons.append("Excellent access - near boundary edge")
            elif edge_distance > 200:
                score -= 1.0
                reasons.append("Interior location - access may be limited")
        
        elif land_use_type in ['agricultural', 'orchards', 'vineyards']:
            # Vegetation quality important
            if ndvi > 0.6:
                score += 3.0
                reasons.append("Excellent vegetation - fertile soil")
            elif ndvi < 0.3:
                score -= 2.0
                reasons.append("Poor vegetation - soil improvement needed")
            
            # Moderate slope acceptable
            if 2 < slope < 12:
                score += 1.0
                reasons.append("Moderate slope - good drainage")
            elif slope > 20:
                score -= 1.5
                reasons.append("Too steep for farming")
        
        elif land_use_type in ['solar_farm', 'energy']:
            # Need flat areas
            if slope < 5:
                score += 2.5
                reasons.append("Flat terrain - ideal for solar panels")
            
            # Southern exposure (in Northern hemisphere)
            # Would need aspect data from DEM
        
        elif land_use_type in ['tourism', 'recreation']:
            # Scenic value - elevation variation good
            if elevation > 200:
                score += 1.5
                reasons.append("Elevated - good views")
            
            # Vegetation for beauty
            if ndvi > 0.5:
                score += 1.0
                reasons.append("Green space - attractive")
        
        # Limit score to 0-10
        final_score = max(0, min(10, score))
        
        # Categorize
        if final_score >= 8:
            category = 'excellent'
        elif final_score >= 6:
            category = 'good'
        elif final_score >= 4:
            category = 'moderate'
        else:
            category = 'poor'
        
        return {
            'score': round(final_score, 2),
            'category': category,
            'reasons': reasons
        }
    
    def _find_best_locations(
        self,
        analyzed_points: List[Dict],
        top_n: int = 5
    ) -> List[Dict]:
        """Find the top N best locations"""
        
        # Sort by suitability score
        sorted_points = sorted(
            analyzed_points,
            key=lambda x: x['suitability_score'],
            reverse=True
        )
        
        return sorted_points[:top_n]
    
    def _create_heatmap_data(
        self,
        analyzed_points: List[Dict]
    ) -> List[List]:
        """Create heatmap data for visualization"""
        
        heatmap = []
        
        for point in analyzed_points:
            heatmap.append([
                point['lat'],
                point['lon'],
                point['suitability_score']
            ])
        
        return heatmap
    
    def _generate_location_recommendations(
        self,
        best_locations: List[Dict],
        land_use_type: str
    ) -> List[str]:
        """Generate human-readable recommendations"""
        
        recommendations = []
        
        for i, loc in enumerate(best_locations, 1):
            reasons = ', '.join(loc['reasons'][:2])  # Top 2 reasons
            
            rec = f"**Location #{i}** (Score: {loc['suitability_score']:.1f}/10) - " \
                  f"Coordinates: ({loc['lat']:.4f}, {loc['lon']:.4f}). {reasons}."
            
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_statistics(
        self,
        analyzed_points: List[Dict]
    ) -> Dict:
        """Calculate summary statistics"""
        
        scores = [p['suitability_score'] for p in analyzed_points]
        
        return {
            'total_points': len(analyzed_points),
            'avg_score': round(np.mean(scores), 2),
            'max_score': round(np.max(scores), 2),
            'min_score': round(np.min(scores), 2),
            'std_score': round(np.std(scores), 2),
            'excellent_count': sum(1 for p in analyzed_points if p['category'] == 'excellent'),
            'good_count': sum(1 for p in analyzed_points if p['category'] == 'good'),
            'moderate_count': sum(1 for p in analyzed_points if p['category'] == 'moderate'),
            'poor_count': sum(1 for p in analyzed_points if p['category'] == 'poor')
        }