# ============================================================================
# FILE: core/analysis_processor.py (UPDATE _extract_all_features METHOD)
# ============================================================================

def _extract_all_features(self, boundary_data: Dict) -> Dict:
    """Extract features from all data sources"""
    
    ee_geometry = boundary_data.get('ee_geometry')
    shapely_geometry = boundary_data.get('geometry')
    centroid = boundary_data.get('centroid')
    
    features = {}
    
    # Extract terrain features (requires EE)
    if self.ee_available and ee_geometry:
        try:
            features['terrain'] = self.terrain_extractor.extract(ee_geometry)
        except Exception as e:
            print(f"Warning: Terrain extraction failed: {e}")
            features['terrain'] = self._get_default_terrain()
    else:
        features['terrain'] = self._get_default_terrain()
    
    # Extract environmental features (requires EE)
    if self.ee_available and ee_geometry:
        try:
            features['environmental'] = self.env_extractor.extract(ee_geometry)
        except Exception as e:
            print(f"Warning: Environmental extraction failed: {e}")
            features['environmental'] = self._get_default_environmental()
    else:
        features['environmental'] = self._get_default_environmental()
    
    # Extract infrastructure features (doesn't require EE)
    try:
        # Pass all available data
        features['infrastructure'] = self.infra_extractor.extract(
            ee_geometry=ee_geometry,
            centroid=centroid,
            geometry=shapely_geometry
        )
    except Exception as e:
        print(f"Warning: Infrastructure extraction failed: {e}")
        features['infrastructure'] = self._get_default_infrastructure()
    
    features['boundary'] = boundary_data
    
    return features

def _get_default_terrain(self) -> Dict:
    """Default terrain features when extraction fails"""
    return {
        'slope_avg': 5.0,
        'slope_min': 0.0,
        'slope_max': 15.0,
        'elevation_avg': 100.0,
        'elevation_min': 90.0,
        'elevation_max': 110.0,
        'elevation_std': 5.0,
        'aspect_degrees': 180.0,
        'aspect_direction': 'S',
        'terrain_classification': 'gentle',
        'buildability_score': 7.0,
        'data_quality': 'default'
    }

def _get_default_environmental(self) -> Dict:
    """Default environmental features when extraction fails"""
    return {
        'ndvi_avg': 0.5,
        'ndvi_min': 0.2,
        'ndvi_max': 0.8,
        'land_cover_distribution': {},
        'dominant_cover': 'grassland',
        'water_occurrence_avg': 5.0,
        'water_occurrence_max': 10.0,
        'flood_risk_level': 'low',
        'flood_risk_percent': 5.0,
        'air_quality_estimate': 'good',
        'environmental_score': 7.0,
        'data_quality': 'default'
    }

def _get_default_infrastructure(self) -> Dict:
    """Default infrastructure features when extraction fails"""
    return {
        'nearest_road_distance': 1000.0,
        'road_type': 'secondary',
        'utilities_available': {
            'water': True,
            'electricity': True,
            'gas': False,
            'sewage': True,
            'internet': True
        },
        'nearby_amenities': {
            'schools': 1,
            'hospitals': 1,
            'shopping': 2,
            'restaurants': 3,
            'parks': 1
        },
        'accessibility_score': 6.0,
        'infrastructure_score': 6.0,
        'data_quality': 'default'
    }
