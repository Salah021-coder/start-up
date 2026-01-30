# ============================================================================
# FILE: data/feature_extraction/environmental_features.py (UPDATED)
# ============================================================================

import ee
from typing import Dict
from data.earth_engine.gee_client import GEEClient

class EnvironmentalFeatureExtractor:
    """Extract environmental features including comprehensive risk assessment"""
    
    def __init__(self):
        self.gee_client = GEEClient()
        self.gee_available = self._check_gee_available()
        
        # Import appropriate risk assessor
        if self.gee_available:
            from data.feature_extraction.risk_assessment import ComprehensiveRiskAssessment
            self.risk_assessor = ComprehensiveRiskAssessment()
        else:
            from data.feature_extraction.fallback_risk_assessment import FallbackRiskAssessment
            self.risk_assessor = FallbackRiskAssessment()
    
    def _check_gee_available(self) -> bool:
        """Check if Earth Engine is available"""
        try:
            ee.String('test').getInfo()
            return True
        except:
            return False
    
    def extract(self, geometry: ee.Geometry = None, terrain_features: Dict = None) -> Dict:
        """Extract all environmental features including comprehensive risks"""
        
        # Initialize results
        results = {}
        
        # Try to get GEE data if available
        if self.gee_available and geometry:
            try:
                # Get vegetation index
                ndvi = self.gee_client.get_ndvi(geometry)
                results.update(ndvi)
                
                # Get land cover
                land_cover = self.gee_client.get_land_cover(geometry)
                results.update(land_cover)
                
                # Get water occurrence
                water = self.gee_client.get_water_occurrence(geometry)
                results.update(water)
                
                # Get air quality estimate
                air_quality = self._estimate_air_quality(land_cover)
                results['air_quality_estimate'] = air_quality
                
                print("✓ Environmental data extracted from Earth Engine")
                
            except Exception as e:
                print(f"⚠ Earth Engine extraction failed: {e}")
                results = self._get_default_environmental()
        else:
            print("ℹ Using default environmental values (GEE not available)")
            results = self._get_default_environmental()
        
        # ALWAYS perform comprehensive risk assessment (works with or without GEE)
        print("Performing comprehensive risk assessment...")
        
        try:
            features_for_risk = {
                'terrain': terrain_features or {},
                'environmental': results,
                'boundary': {}  # Will be filled by analyzer
            }
            
            comprehensive_risks = self.risk_assessor.assess_all_risks(
                geometry=geometry,
                features=features_for_risk
            )
            
            results['comprehensive_risks'] = comprehensive_risks
            
            # Legacy compatibility - extract flood risk
            flood_risk = comprehensive_risks.get('flood', {})
            results['flood_risk_level'] = flood_risk.get('level', 'unknown')
            results['flood_risk_percent'] = flood_risk.get('affected_area_percent', 0)
            
            print("✓ Comprehensive risk assessment completed")
            
        except Exception as e:
            print(f"⚠ Risk assessment failed: {e}")
            # Provide minimal risk data
            results['comprehensive_risks'] = self._get_minimal_risks()
            results['flood_risk_level'] = 'unknown'
            results['flood_risk_percent'] = 0
        
        # Calculate environmental score
        results['environmental_score'] = self._calculate_env_score(results)
        results['data_quality'] = 'gee' if self.gee_available else 'estimated'
        
        return results
    
    def _estimate_air_quality(self, land_cover: Dict) -> str:
        """Estimate air quality based on land cover"""
        dominant = land_cover.get('dominant_cover', 'unknown')
        
        if dominant in ['tree_cover', 'grassland', 'wetland']:
            return 'good'
        elif dominant in ['cropland', 'shrubland']:
            return 'moderate'
        elif dominant in ['built_up', 'industrial']:
            return 'poor'
        else:
            return 'unknown'
    
    def _calculate_env_score(self, env_data: Dict) -> float:
        """Calculate overall environmental score"""
        score = 5.0
        
        # Good vegetation increases score
        ndvi_val = env_data.get('ndvi_avg', 0.5)
        score += (ndvi_val - 0.3) * 5
        
        # Comprehensive risk affects score
        if 'comprehensive_risks' in env_data:
            overall_risk = env_data['comprehensive_risks'].get('overall', {})
            avg_severity = overall_risk.get('average_severity', 2.5)
            # Lower severity = higher score
            score += (3 - avg_severity) * 1.5
        
        return max(0, min(10, score))
    
    def _get_default_environmental(self) -> Dict:
        """Default environmental values when GEE unavailable"""
        return {
            'ndvi_avg': 0.5,
            'ndvi_min': 0.2,
            'ndvi_max': 0.8,
            'land_cover_distribution': {},
            'dominant_cover': 'grassland',
            'water_occurrence_avg': 5.0,
            'water_occurrence_max': 10.0,
            'air_quality_estimate': 'moderate'
        }
    
    def _get_minimal_risks(self) -> Dict:
        """Minimal risk data when assessment fails"""
        return {
            'flood': {'level': 'unknown', 'severity': 0, 'score': 0, 'description': 'Not assessed'},
            'landslide': {'level': 'unknown', 'severity': 0, 'score': 0, 'description': 'Not assessed'},
            'erosion': {'level': 'unknown', 'severity': 0, 'score': 0, 'description': 'Not assessed'},
            'seismic': {'level': 'unknown', 'severity': 0, 'score': 0, 'description': 'Not assessed'},
            'drought': {'level': 'unknown', 'severity': 0, 'score': 0, 'description': 'Not assessed'},
            'wildfire': {'level': 'unknown', 'severity': 0, 'score': 0, 'description': 'Not assessed'},
            'subsidence': {'level': 'unknown', 'severity': 0, 'score': 0, 'description': 'Not assessed'},
            'overall': {'level': 'unknown', 'average_severity': 0, 'high_risk_count': 0, 'medium_risk_count': 0},
            'summary': ['⚠️ Risk assessment not available'],
            'mitigation': []
        }
