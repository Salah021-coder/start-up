from typing import Dict, List
import numpy as np

class RecommendationEngine:
    """Generate final land use recommendations"""
    
    LAND_USE_TYPES = [
        'residential',
        'commercial',
        'agricultural',
        'industrial',
        'mixed_use',
        'recreational',
        'conservation'
    ]
    
    def generate_recommendations(
        self,
        features: Dict,
        scores: Dict,
        criteria: Dict
    ) -> List[Dict]:
        """
        Generate ranked recommendations for land use
        """
        recommendations = []
        
        for land_use in self.LAND_USE_TYPES:
            suitability = self._calculate_suitability(
                land_use,
                features,
                scores
            )
            
            if suitability['score'] > 5.0:  # Only include viable options
                recommendations.append({
                    'rank': 0,  # Will be set after sorting
                    'usage_type': land_use,
                    'suitability_score': suitability['score'],
                    'confidence': suitability['confidence'],
                    'supporting_factors': suitability['factors'],
                    'concerns': suitability['concerns'],
                    'estimated_roi': suitability.get('roi', 'N/A')
                })
        
        # Sort by score and assign ranks
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        for i, rec in enumerate(recommendations):
            rec['rank'] = i + 1
        
        return recommendations[:5]  # Return top 5
    
    def _calculate_suitability(
        self,
        land_use: str,
        features: Dict,
        scores: Dict
    ) -> Dict:
        """Calculate suitability score for specific land use"""
        
        # This is a simplified version
        # In production, this would use sophisticated algorithms
        
        terrain = features.get('terrain', {})
        infra = features.get('infrastructure', {})
        env = features.get('environmental', {})
        
        factors = []
        concerns = []
        base_score = 5.0
        
        if land_use == 'residential':
            # Check slope
            slope = terrain.get('slope_avg', 999)
            if slope < 5:
                base_score += 2.0
                factors.append(f"Gentle slope ({slope:.1f}°)")
            elif slope > 15:
                base_score -= 1.5
                concerns.append(f"Steep slope ({slope:.1f}°)")
            
            # Check road access
            road_dist = infra.get('nearest_road_distance', 999999)
            if road_dist < 500:
                base_score += 1.5
                factors.append(f"Excellent road access ({road_dist:.0f}m)")
            elif road_dist > 2000:
                base_score -= 1.0
                concerns.append(f"Limited road access ({road_dist/1000:.1f}km)")
            
            # Check flood risk
            flood = env.get('flood_risk_percent', 0)
            if flood < 10:
                base_score += 1.0
                factors.append("Low flood risk")
            elif flood > 30:
                base_score -= 1.5
                concerns.append(f"Flood risk in {flood:.0f}% of area")
        
        elif land_use == 'agricultural':
            # Check soil and vegetation
            ndvi = env.get('ndvi_avg', 0)
            if ndvi > 0.6:
                base_score += 2.0
                factors.append("High vegetation index")
            
            slope = terrain.get('slope_avg', 999)
            if slope < 8:
                base_score += 1.5
                factors.append("Suitable slope for farming")
        
        # Ensure score is between 0 and 10
        final_score = max(0, min(10, base_score))
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(features)
        
        return {
            'score': final_score,
            'confidence': confidence,
            'factors': factors,
            'concerns': concerns,
            'roi': self._estimate_roi(land_use, final_score)
        }
    
    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate confidence level based on data completeness"""
        # Simple confidence calculation
        # In production, this would be more sophisticated
        confidence = 0.7  # Base confidence
        
        if features.get('terrain', {}).get('data_quality') == 'high':
            confidence += 0.1
        if features.get('environmental', {}).get('data_quality') == 'high':
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _estimate_roi(self, land_use: str, score: float) -> str:
        """Estimate return on investment category"""
        if score >= 8:
            return "High"
        elif score >= 6:
            return "Medium"
        else:
            return "Low"