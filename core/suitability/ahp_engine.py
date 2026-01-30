# ============================================================================
# FILE: core/suitability/ahp_engine.py
# AHP (Analytic Hierarchy Process) Engine
# ============================================================================

from typing import Dict, List, Optional
import logging
import numpy as np
from config.criteria_config import CriteriaConfig

logger = logging.getLogger(__name__)


class AHPEngine:
    """
    Analytic Hierarchy Process (AHP) implementation
    
    RESPONSIBILITIES:
    - Calculate suitability scores for each criterion
    - Apply AHP methodology with criteria weights
    - Aggregate scores into overall suitability
    - Provide criterion-level breakdown
    
    DOES NOT:
    - Extract features (uses provided features)
    - Select criteria (uses provided criteria)
    - Make land-use recommendations (that's recommender's job)
    """
    
    def __init__(self):
        """Initialize AHP engine"""
        self.config = CriteriaConfig()
        
        # Consistency threshold for AHP
        self.consistency_threshold = 0.1  # CR < 0.1 is acceptable
    
    def auto_select_criteria(
        self,
        features: Dict,
        risk_result = None
    ) -> Dict:
        """
        Auto-select criteria based on features
        
        This is a convenience method that uses CriteriaEngine logic
        
        Args:
            features: Extracted features
            risk_result: Optional risk assessment result
            
        Returns:
            Selected criteria
        """
        # Extract location characteristics from features
        infra = features.get('infrastructure', {})
        
        location_data = {
            'urbanization_level': infra.get('urbanization_level', 'suburban'),
            'population_density': infra.get('population_density', 500),
            'nearest_road_distance': infra.get('nearest_road_distance', 1000)
        }
        
        # Use config to select criteria
        criteria = self.config.auto_select_criteria(location_data)
        
        return criteria
    
    def calculate_suitability(
        self,
        features: Dict,
        criteria: Dict
    ) -> Dict:
        """
        Calculate suitability using AHP
        
        Args:
            features: Extracted features (terrain, environmental, infrastructure)
            criteria: Criteria weights (from criteria engine)
            
        Returns:
            Dict with:
                - criterion_scores: Individual criterion scores (0-10)
                - weighted_scores: Weighted criterion contributions
                - overall_score: Final AHP score (0-10)
                - category_scores: Scores by category
                - consistency_ratio: AHP consistency measure
        """
        logger.info("Calculating AHP suitability scores")
        
        # Flatten criteria for easier processing
        flat_criteria = self._flatten_criteria(criteria)
        
        logger.debug(f"Evaluating {len(flat_criteria)} criteria")
        
        # Score each criterion
        criterion_scores = self._score_all_criteria(features, flat_criteria)
        
        # Apply weights
        weighted_scores = {}
        for criterion, score in criterion_scores.items():
            weight = flat_criteria.get(criterion, 0)
            weighted_scores[criterion] = score * weight
        
        # Calculate overall score
        overall_score = sum(weighted_scores.values())
        
        # Calculate category scores (for breakdown)
        category_scores = self._calculate_category_scores(
            criterion_scores,
            criteria
        )
        
        # Calculate consistency ratio (simplified)
        consistency_ratio = self._calculate_consistency_ratio(criteria)
        
        result = {
            'criterion_scores': criterion_scores,
            'weighted_scores': weighted_scores,
            'overall_score': round(overall_score, 2),
            'category_scores': category_scores,
            'consistency_ratio': consistency_ratio,
            'is_consistent': consistency_ratio < self.consistency_threshold,
            'methodology': 'AHP'
        }
        
        logger.info(
            f"AHP calculation complete: overall score {overall_score:.2f}/10, "
            f"CR={consistency_ratio:.3f}"
        )
        
        return result
    
    def _score_all_criteria(
        self,
        features: Dict,
        flat_criteria: Dict
    ) -> Dict:
        """
        Score all criteria based on features
        
        Args:
            features: Feature dict
            flat_criteria: Flattened criteria with weights
            
        Returns:
            Dict mapping criterion name to score (0-10)
        """
        scores = {}
        
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        # Score each criterion
        for criterion_key in flat_criteria.keys():
            try:
                score = self._score_single_criterion(
                    criterion_key,
                    terrain,
                    env,
                    infra
                )
                scores[criterion_key] = score
                
            except Exception as e:
                logger.warning(f"Failed to score criterion '{criterion_key}': {e}")
                scores[criterion_key] = 5.0  # Neutral fallback
        
        return scores
    
    def _score_single_criterion(
        self,
        criterion_key: str,
        terrain: Dict,
        env: Dict,
        infra: Dict
    ) -> float:
        """
        Score a single criterion (0-10 scale)
        
        Args:
            criterion_key: Criterion identifier (e.g., 'terrain_slope')
            terrain: Terrain features
            env: Environmental features
            infra: Infrastructure features
            
        Returns:
            Score between 0-10
        """
        # Parse criterion key (format: category_criterion)
        parts = criterion_key.split('_', 1)
        if len(parts) != 2:
            logger.warning(f"Invalid criterion key format: {criterion_key}")
            return 5.0
        
        category, criterion = parts
        
        # === TERRAIN CRITERIA ===
        if category == 'terrain':
            if criterion == 'slope':
                return self._score_slope(terrain.get('slope_avg', 0))
            
            elif criterion == 'elevation':
                return self._score_elevation(terrain.get('elevation_avg', 100))
            
            elif criterion == 'aspect':
                return self._score_aspect(terrain.get('aspect_avg', 180))
        
        # === ACCESSIBILITY CRITERIA ===
        elif category == 'accessibility':
            if criterion == 'road' or criterion == 'proximity':
                return self._score_road_distance(infra.get('nearest_road_distance', 1000))
            
            elif criterion == 'public' or criterion == 'transport':
                return infra.get('public_transport_score', 5.0)
            
            elif criterion == 'motorway' or criterion == 'access':
                return self._score_motorway_distance(infra.get('motorway_distance', 50000))
        
        # === URBAN CONTEXT ===
        elif category == 'urban':
            if criterion == 'proximity':
                urbanization = infra.get('urbanization_level', 'suburban')
                return self._score_urbanization(urbanization, 'proximity')
            
            elif criterion == 'population' or criterion == 'density':
                return self._score_population_density(infra.get('population_density', 500))
            
            elif criterion == 'development' or criterion == 'pressure':
                pressure = infra.get('development_pressure', 'medium')
                return self._score_development_pressure(pressure)
        
        # === AMENITIES ===
        elif category == 'amenities':
            if criterion == 'schools':
                return self._score_amenity_count(infra.get('schools_count_3km', 0), ideal=3, max_good=10)
            
            elif criterion == 'healthcare':
                hospitals = infra.get('hospitals_count_5km', 0)
                clinics = infra.get('clinics_count_2km', 0)
                return self._score_amenity_count(hospitals + clinics, ideal=2, max_good=5)
            
            elif criterion == 'shopping':
                return self._score_amenity_count(infra.get('supermarkets_count_2km', 0), ideal=2, max_good=5)
            
            elif criterion == 'parks':
                # Use green space as proxy
                green_space = env.get('green_space_percent', 20)
                return min(10, green_space / 5)
        
        # === INFRASTRUCTURE ===
        elif category == 'infrastructure':
            if criterion == 'utilities' or criterion == 'complete':
                return self._score_utilities(infra.get('utilities_available', 3))
            
            elif criterion == 'internet' or criterion == 'quality':
                return 8.0 if infra.get('internet_fiber', False) else 4.0
        
        # === ENVIRONMENT ===
        elif category == 'environment':
            if criterion == 'flood' or criterion == 'risk':
                # Lower flood risk = higher score (inverted)
                return 10.0  # Will be overridden by risk engine
            
            elif criterion == 'air' or criterion == 'quality':
                # Estimate based on urbanization
                urbanization = infra.get('urbanization_level', 'suburban')
                if urbanization in ['remote', 'rural']:
                    return 9.0
                elif urbanization == 'suburban':
                    return 7.0
                else:
                    return 5.0
            
            elif criterion == 'noise' or criterion == 'level':
                road_dist = infra.get('nearest_road_distance', 1000)
                return min(10, road_dist / 200)
        
        # === AGRICULTURAL CRITERIA ===
        elif category == 'soil':
            # Estimate soil quality from NDVI
            ndvi = env.get('ndvi_avg', 0.5)
            return min(10, ndvi * 15)
        
        elif category == 'water':
            if criterion == 'irrigation' or criterion == 'access':
                water_occurrence = env.get('water_occurrence_avg', 0)
                return min(10, water_occurrence / 10) if water_occurrence > 0 else 3.0
        
        elif category == 'agricultural':
            if criterion == 'potential':
                # Combine NDVI and slope
                ndvi = env.get('ndvi_avg', 0.5)
                slope = terrain.get('slope_avg', 5)
                
                ndvi_score = ndvi * 10
                slope_penalty = max(0, (slope - 10) / 2)
                
                return max(0, min(10, ndvi_score - slope_penalty))
        
        # Default: neutral score
        logger.debug(f"No scoring rule for {criterion_key}, using neutral score")
        return 5.0
    
    # === SCORING FUNCTIONS ===
    
    def _score_slope(self, slope: float) -> float:
        """Score slope (flatter = better for most uses)"""
        if slope < 3:
            return 10.0
        elif slope < 8:
            return 8.5
        elif slope < 15:
            return 6.0
        elif slope < 25:
            return 4.0
        elif slope < 35:
            return 2.0
        else:
            return 1.0
    
    def _score_elevation(self, elevation: float) -> float:
        """Score elevation (moderate is often best)"""
        if 100 <= elevation <= 500:
            return 9.0
        elif 50 <= elevation <= 1000:
            return 7.5
        elif 0 <= elevation <= 2000:
            return 6.0
        else:
            return 4.0
    
    def _score_aspect(self, aspect: float) -> float:
        """Score aspect (orientation) - simplified"""
        # In Northern Hemisphere, south-facing is generally preferred
        # 180° = south
        deviation = abs(aspect - 180)
        
        if deviation < 45:
            return 9.0  # South-facing
        elif deviation < 90:
            return 7.0  # Southeast/Southwest
        elif deviation < 135:
            return 6.0  # East/West
        else:
            return 5.0  # North-facing
    
    def _score_road_distance(self, distance: float) -> float:
        """Score road proximity (closer = better)"""
        if distance < 200:
            return 10.0
        elif distance < 500:
            return 8.5
        elif distance < 1000:
            return 7.0
        elif distance < 2000:
            return 5.0
        elif distance < 5000:
            return 3.0
        else:
            return 1.0
    
    def _score_motorway_distance(self, distance: float) -> float:
        """Score motorway proximity"""
        if distance < 2000:
            return 9.0
        elif distance < 5000:
            return 8.0
        elif distance < 10000:
            return 7.0
        elif distance < 20000:
            return 5.0
        else:
            return 3.0
    
    def _score_urbanization(self, level: str, context: str) -> float:
        """Score urbanization level (depends on context)"""
        scores = {
            'city_center': 9.0,
            'urban': 8.5,
            'suburban': 8.0,
            'rural': 6.0,
            'remote': 3.0
        }
        return scores.get(level, 5.0)
    
    def _score_population_density(self, density: float) -> float:
        """Score population density (moderate is often best for residential)"""
        if 500 <= density <= 2000:
            return 9.0
        elif 200 <= density <= 5000:
            return 7.5
        elif density < 100:
            return 5.0
        else:
            return 6.0
    
    def _score_development_pressure(self, pressure: str) -> float:
        """Score development pressure"""
        scores = {
            'very_high': 9.0,
            'high': 8.0,
            'medium': 7.0,
            'low': 5.0,
            'very_low': 3.0
        }
        return scores.get(pressure, 5.0)
    
    def _score_amenity_count(self, count: int, ideal: int, max_good: int) -> float:
        """Score amenity availability"""
        if count >= ideal:
            return min(10.0, 7.0 + (count - ideal) * 0.5)
        elif count > 0:
            return 5.0 + (count / ideal) * 2.0
        else:
            return 3.0
    
    def _score_utilities(self, available_count: int) -> float:
        """Score utility availability (out of 5 typical utilities)"""
        return min(10.0, (available_count / 5) * 10)
    
    def _calculate_category_scores(
        self,
        criterion_scores: Dict,
        criteria: Dict
    ) -> Dict:
        """
        Calculate average scores by category
        
        Args:
            criterion_scores: Individual criterion scores
            criteria: Nested criteria dict
            
        Returns:
            Dict mapping category to average score
        """
        category_scores = {}
        
        for category, weights in criteria.items():
            if not isinstance(weights, dict):
                continue
            
            category_criteria = [
                f"{category}_{criterion}"
                for criterion in weights.keys()
            ]
            
            scores = [
                criterion_scores.get(key, 5.0)
                for key in category_criteria
            ]
            
            if scores:
                category_scores[category] = round(sum(scores) / len(scores), 2)
        
        return category_scores
    
    def _calculate_consistency_ratio(self, criteria: Dict) -> float:
        """
        Calculate AHP consistency ratio (simplified)
        
        For full AHP, this would use eigenvalue method
        For our purposes, we use a simplified approximation
        
        Returns:
            Consistency ratio (lower = more consistent)
        """
        # Simplified: check if weights are relatively balanced
        flat = self._flatten_criteria(criteria)
        weights = list(flat.values())
        
        if not weights:
            return 0.0
        
        # Calculate coefficient of variation
        mean_weight = sum(weights) / len(weights)
        variance = sum((w - mean_weight) ** 2 for w in weights) / len(weights)
        std_dev = variance ** 0.5
        
        cv = std_dev / mean_weight if mean_weight > 0 else 0
        
        # Convert to CR-like metric (0-1 scale)
        cr = min(1.0, cv)
        
        return round(cr, 3)
    
    def _flatten_criteria(self, criteria: Dict) -> Dict:
        """Flatten nested criteria into single dict"""
        flat = {}
        for category, weights in criteria.items():
            if isinstance(weights, dict):
                for criterion, weight in weights.items():
                    key = f"{category}_{criterion}"
                    flat[key] = weight
        return flat
