
from typing import Dict
import numpy as np

class ScoreAggregator:
    """Aggregate AHP and ML scores"""
    
    def __init__(self, ahp_weight: float = 0.4, ml_weight: float = 0.6):
        self.ahp_weight = ahp_weight
        self.ml_weight = ml_weight
    
    def aggregate(
        self,
        ahp_results: Dict,
        ml_results: Dict,
        features: Dict
    ) -> Dict:
        """Aggregate multiple scoring methods"""
        
        # Get scores
        ahp_score = ahp_results.get('total_score', 5.0)
        ml_score = ml_results.get('suitability_score', 5.0)
        
        # Weighted aggregation
        final_score = (ahp_score * self.ahp_weight) + (ml_score * self.ml_weight)
        
        # Calculate overall confidence
        confidence = self._aggregate_confidence(ahp_results, ml_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(final_score, features)
        
        # Assess risks
        risk_assessment = self._assess_risks(features)
        
        return {
            'overall_score': round(final_score, 2),
            'ahp_score': round(ahp_score, 2),
            'ml_score': round(ml_score, 2),
            'confidence': round(confidence, 3),
            'recommendations': recommendations,
            'risk_assessment': risk_assessment,
            'score_breakdown': {
                'ahp_contribution': round(ahp_score * self.ahp_weight, 2),
                'ml_contribution': round(ml_score * self.ml_weight, 2)
            }
        }
    
    def _aggregate_confidence(self, ahp_results: Dict, ml_results: Dict) -> float:
        """Aggregate confidence scores"""
        ahp_conf = 0.9 if ahp_results.get('is_consistent', False) else 0.7
        ml_conf = ml_results.get('confidence', 0.7)
        
        return (ahp_conf + ml_conf) / 2
    
    def _generate_recommendations(self, score: float, features: Dict) -> list:
        """Generate usage recommendations based on score and features"""
        from core.recommendation_engine import RecommendationEngine
        
        rec_engine = RecommendationEngine()
        return rec_engine.generate_recommendations(features, {'overall_score': score}, {})
    
    def _assess_risks(self, features: Dict) -> Dict:
        """Assess development risks"""
        risks = []
        risk_level = 'low'
        
        # Environmental risks
        env = features.get('environmental', {})
        if env.get('flood_risk_percent', 0) > 30:
            risks.append('High flood risk')
            risk_level = 'high'
        
        # Terrain risks
        terrain = features.get('terrain', {})
        if terrain.get('slope_avg', 0) > 15:
            risks.append('Steep slopes may increase construction costs')
            if risk_level == 'low':
                risk_level = 'medium'
        
        # Infrastructure risks
        infra = features.get('infrastructure', {})
        if infra.get('nearest_road_distance', 0) > 2000:
            risks.append('Limited road access')
            if risk_level == 'low':
                risk_level = 'medium'
        
        return {
            'level': risk_level,
            'risks': risks,
            'risk_count': len(risks)
        }
