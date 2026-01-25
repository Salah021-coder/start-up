from typing import Dict, List
import numpy as np
from config.criteria_config import CriteriaConfig

class CriteriaEngine:
    """Auto-select and weight evaluation criteria"""
    
    def __init__(self):
        self.criteria_config = CriteriaConfig()
    
    def auto_select_criteria(
        self, 
        boundary_data: Dict,
        location_features: Dict = None,
        target_use: str = None
    ) -> Dict:
        """
        Automatically select relevant criteria based on:
        - Location characteristics
        - Detected features
        - Target use case (if specified)
        """
        
        # If target use is specified, use predefined criteria
        if target_use:
            base_criteria = self.criteria_config.get_criteria_for_use(target_use)
        else:
            # Analyze location to determine best criteria
            base_criteria = self._analyze_location_criteria(
                boundary_data, 
                location_features
            )
        
        # Adjust weights based on detected features
        adjusted_criteria = self._adjust_criteria_weights(
            base_criteria,
            location_features or {}
        )
        
        return {
            'criteria': adjusted_criteria,
            'flat_criteria': self.criteria_config.flatten_criteria(adjusted_criteria),
            'selection_method': 'auto' if not target_use else 'manual',
            'target_use': target_use or 'mixed'
        }
    
    def _analyze_location_criteria(
        self, 
        boundary_data: Dict,
        location_features: Dict
    ) -> Dict:
        """
        Analyze location to determine most appropriate criteria
        """
        # Default to residential for now
        # In production, this would analyze:
        # - Surrounding land use
        # - Zoning regulations
        # - Population density
        # - Infrastructure availability
        
        return self.criteria_config.RESIDENTIAL_CRITERIA
    
    def _adjust_criteria_weights(
        self,
        base_criteria: Dict,
        features: Dict
    ) -> Dict:
        """
        Adjust criteria weights based on detected features
        """
        adjusted = base_criteria.copy()
        
        # Example adjustments based on features
        # This would be more sophisticated in production
        
        if features.get('slope_avg', 0) > 15:
            # High slope - increase terrain importance
            if 'terrain' in adjusted:
                for key in adjusted['terrain']:
                    adjusted['terrain'][key] *= 1.2
        
        if features.get('flood_risk_level') == 'high':
            # High flood risk - increase environmental importance
            if 'environmental' in adjusted:
                for key in adjusted['environmental']:
                    adjusted['environmental'][key] *= 1.3
        
        # Normalize weights to sum to 1.0
        adjusted = self._normalize_weights(adjusted)
        
        return adjusted
    
    def _normalize_weights(self, criteria: Dict) -> Dict:
        """Normalize all weights to sum to 1.0"""
        total = sum(
            sum(weights.values()) 
            for weights in criteria.values()
        )
        
        normalized = {}
        for category, weights in criteria.items():
            normalized[category] = {
                key: value / total 
                for key, value in weights.items()
            }
        
        return normalized
    
    def get_criteria_explanation(self, criteria: Dict) -> List[Dict]:
        """
        Generate human-readable explanations for selected criteria
        """
        explanations = []
        
        for category, weights in criteria.items():
            for criterion, weight in weights.items():
                explanations.append({
                    'category': category,
                    'criterion': criterion,
                    'weight': weight,
                    'importance': self._weight_to_importance(weight),
                    'explanation': self._get_criterion_explanation(category, criterion)
                })
        
        return sorted(explanations, key=lambda x: x['weight'], reverse=True)
    
    def _weight_to_importance(self, weight: float) -> str:
        """Convert numerical weight to importance level"""
        if weight >= 0.15:
            return 'Very High'
        elif weight >= 0.10:
            return 'High'
        elif weight >= 0.05:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_criterion_explanation(self, category: str, criterion: str) -> str:
        """Get explanation for a specific criterion"""
        explanations = {
            'terrain_slope': 'Gentle slopes are easier and cheaper to build on',
            'terrain_elevation': 'Elevation affects accessibility and views',
            'infrastructure_road_proximity': 'Nearby roads improve accessibility and value',
            'environmental_flood_risk': 'Low flood risk reduces insurance costs and damage',
            'soil_fertility': 'Fertile soil is essential for agricultural productivity',
            'water_irrigation_potential': 'Water availability is critical for agriculture',
        }
        
        key = f"{category}_{criterion}"
        return explanations.get(key, f"Evaluates {criterion} in {category}")