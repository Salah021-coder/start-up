import ee
from typing import Dict
from data.earth_engine.gee_client import GEEClient
from data.feature_extraction.risk_assessment import ComprehensiveRiskAssessment

class EnvironmentalFeatureExtractor:
    """Extract environmental features including comprehensive risk assessment"""
    
    def __init__(self):
        self.gee_client = GEEClient()
        self.risk_assessor = ComprehensiveRiskAssessment()
    
    def extract(self, geometry: ee.Geometry, terrain_features: Dict = None) -> Dict:
        """Extract all environmental features including comprehensive risks"""
        
        # Get vegetation index
        ndvi = self.gee_client.get_ndvi(geometry)
        
        # Get land cover
        land_cover = self.gee_client.get_land_cover(geometry)
        
        # Get water occurrence
        water = self.gee_client.get_water_occurrence(geometry)
        
        # Get air quality estimate (simplified)
        air_quality = self._estimate_air_quality(land_cover)
        
        # Comprehensive risk assessment
        # Need to pass terrain features if available
        features_for_risk = {
            'terrain': terrain_features or {},
            'environmental': {**ndvi, **land_cover, **water}
        }
        
        comprehensive_risks = self.risk_assessor.assess_all_risks(geometry, features_for_risk)
        
        # Legacy compatibility - keep old flood risk format
        flood_risk = comprehensive_risks.get('flood', {})
        
        return {
            **ndvi,
            **land_cover,
            **water,
            'flood_risk_level': flood_risk.get('level', 'unknown'),
            'flood_risk_percent': flood_risk.get('affected_area_percent', 0),
            'air_quality_estimate': air_quality,
            'environmental_score': self._calculate_env_score(ndvi, flood_risk),
            'comprehensive_risks': comprehensive_risks,  # NEW: All risks included
            'data_quality': 'high'
        }
    
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
    
    def _calculate_env_score(self, ndvi: Dict, flood_risk: Dict) -> float:
        """Calculate overall environmental score"""
        score = 5.0
        
        # Good vegetation increases score
        ndvi_val = ndvi.get('ndvi_avg', 0)
        score += (ndvi_val - 0.3) * 5
        
        # Flood risk decreases score
        risk_level = flood_risk.get('level', 'low')
        if risk_level == 'very_low' or risk_level == 'low':
            score += 2
        elif risk_level == 'very_high':
            score -= 3
        elif risk_level == 'high':
            score -= 2
        
        return max(0, min(10, score))
