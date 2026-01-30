# ============================================================================
# FILE: core/criteria_engine.py
# Automatic Criteria Selection Engine
# ============================================================================

from typing import Dict, List, Optional
import logging
from config.criteria_config import CriteriaConfig

logger = logging.getLogger(__name__)


class CriteriaEngine:
    """
    Automatically select evaluation criteria based on location
    
    RESPONSIBILITIES:
    - Analyze location characteristics
    - Select appropriate AHP criteria
    - Adjust weights based on context
    - Return configured criteria for analysis
    
    DOES NOT:
    - Perform actual scoring (that's AHP engine's job)
    - Extract features (that's feature extractors' job)
    - Make land-use recommendations (that's recommender's job)
    """
    
    def __init__(self):
        """Initialize criteria engine"""
        self.config = CriteriaConfig()
    
    def auto_select_criteria(
        self,
        boundary_data: Dict,
        initial_features: Optional[Dict] = None
    ) -> Dict:
        """
        Automatically select criteria based on boundary location
        
        Args:
            boundary_data: Boundary with centroid and area
            initial_features: Optional initial feature extraction (if available)
            
        Returns:
            Dict with:
                - criteria: Selected criteria with weights
                - land_use_hint: Suggested primary land use
                - reasoning: Why these criteria were selected
        """
        logger.info("Auto-selecting evaluation criteria")
        
        # Extract location context
        centroid = boundary_data.get('centroid', [0, 0])
        area_km2 = boundary_data.get('area_km2', 0)
        
        lon, lat = centroid
        
        logger.debug(f"Location: {lat:.4f}°N, {lon:.4f}°E, Area: {area_km2:.2f} km²")
        
        # Analyze location characteristics
        location_context = self._analyze_location_context(
            lat, lon, area_km2, initial_features
        )
        
        # Select base criteria based on context
        base_criteria = self._select_base_criteria(location_context)
        
        # Adjust criteria weights based on specifics
        adjusted_criteria = self._adjust_criteria_weights(
            base_criteria,
            location_context,
            area_km2
        )
        
        # Suggest primary land use
        land_use_hint = self._suggest_land_use(location_context, area_km2)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            location_context,
            land_use_hint,
            adjusted_criteria
        )
        
        logger.info(
            f"Criteria selected: {len(self._flatten_criteria(adjusted_criteria))} criteria, "
            f"suggested use: {land_use_hint}"
        )
        
        return {
            'criteria': adjusted_criteria,
            'land_use_hint': land_use_hint,
            'reasoning': reasoning,
            'location_context': location_context
        }
    
    def _analyze_location_context(
        self,
        lat: float,
        lon: float,
        area_km2: float,
        initial_features: Optional[Dict]
    ) -> Dict:
        """
        Analyze location to understand context
        
        Returns:
            Dict with location characteristics
        """
        context = {
            'latitude': lat,
            'longitude': lon,
            'area_km2': area_km2
        }
        
        # Geographic region (simplified for Algeria)
        if lat > 36:
            context['region'] = 'northern_coast'
            context['climate'] = 'mediterranean'
        elif lat > 34:
            context['region'] = 'tell_atlas'
            context['climate'] = 'semi_arid'
        elif lat > 32:
            context['region'] = 'high_plateaus'
            context['climate'] = 'arid'
        else:
            context['region'] = 'sahara'
            context['climate'] = 'desert'
        
        # Proximity to major cities (rough estimates)
        algiers_dist = self._estimate_city_distance(lat, lon, 36.7538, 3.0588)
        oran_dist = self._estimate_city_distance(lat, lon, 35.6969, -0.6331)
        constantine_dist = self._estimate_city_distance(lat, lon, 36.3650, 6.6147)
        
        nearest_city_dist = min(algiers_dist, oran_dist, constantine_dist)
        context['nearest_major_city_km'] = nearest_city_dist
        
        # Estimate urbanization (will be refined by infrastructure extraction)
        if nearest_city_dist < 10:
            context['estimated_urbanization'] = 'urban'
        elif nearest_city_dist < 30:
            context['estimated_urbanization'] = 'suburban'
        elif nearest_city_dist < 100:
            context['estimated_urbanization'] = 'rural'
        else:
            context['estimated_urbanization'] = 'remote'
        
        # Area size classification
        if area_km2 < 0.01:  # < 1 hectare
            context['size_class'] = 'small_plot'
        elif area_km2 < 0.1:  # 1-10 hectares
            context['size_class'] = 'medium_plot'
        elif area_km2 < 1.0:  # 10-100 hectares
            context['size_class'] = 'large_plot'
        else:
            context['size_class'] = 'very_large_area'
        
        # If initial features available, use them
        if initial_features:
            if 'infrastructure' in initial_features:
                infra = initial_features['infrastructure']
                context['urbanization_level'] = infra.get('urbanization_level', context['estimated_urbanization'])
                context['population_density'] = infra.get('population_density', 0)
            
            if 'terrain' in initial_features:
                terrain = initial_features['terrain']
                context['avg_slope'] = terrain.get('slope_avg', None)
        
        return context
    
    def _select_base_criteria(
        self,
        context: Dict
    ) -> Dict:
        """
        Select base criteria set based on location context
        
        Returns:
            Base criteria dictionary
        """
        urbanization = context.get('urbanization_level') or context.get('estimated_urbanization', 'suburban')
        climate = context.get('climate', 'semi_arid')
        size_class = context.get('size_class', 'medium_plot')
        
        # Urban/suburban areas -> residential/commercial focus
        if urbanization in ['urban', 'suburban']:
            logger.debug("Selecting urban/suburban criteria (residential focus)")
            base_criteria = self.config.RESIDENTIAL_CRITERIA.copy()
            
        # Rural areas -> agricultural potential
        elif urbanization == 'rural' and climate in ['mediterranean', 'semi_arid']:
            logger.debug("Selecting rural criteria (agricultural focus)")
            base_criteria = self.config.AGRICULTURAL_CRITERIA.copy()
            
        # Remote/desert areas -> mixed use with emphasis on accessibility
        else:
            logger.debug("Selecting remote area criteria (mixed use)")
            # Use residential as base but will adjust weights
            base_criteria = self.config.RESIDENTIAL_CRITERIA.copy()
        
        return base_criteria
    
    def _adjust_criteria_weights(
        self,
        base_criteria: Dict,
        context: Dict,
        area_km2: float
    ) -> Dict:
        """
        Adjust criteria weights based on specific context
        
        Args:
            base_criteria: Base criteria from selection
            context: Location context
            area_km2: Area size
            
        Returns:
            Adjusted criteria dictionary
        """
        adjusted = self._deep_copy_criteria(base_criteria)
        
        urbanization = context.get('urbanization_level') or context.get('estimated_urbanization', 'suburban')
        nearest_city_km = context.get('nearest_major_city_km', 50)
        
        # Adjustment 1: If remote, increase accessibility weight
        if nearest_city_km > 50 or urbanization == 'remote':
            logger.debug("Increasing accessibility weights (remote location)")
            if 'accessibility' in adjusted:
                for key in adjusted['accessibility']:
                    adjusted['accessibility'][key] *= 1.5
        
        # Adjustment 2: If large area, consider agricultural potential
        if area_km2 > 1.0:
            logger.debug("Area > 1 km² - considering agricultural potential")
            # Add agricultural criteria if not present
            if 'soil' not in adjusted:
                adjusted['agricultural_potential'] = {
                    'soil_suitability': 0.10,
                    'water_access': 0.08
                }
        
        # Adjustment 3: If small plot in urban area, focus on buildability
        if area_km2 < 0.01 and urbanization == 'urban':
            logger.debug("Small urban plot - emphasizing buildability")
            if 'terrain' in adjusted:
                for key in adjusted['terrain']:
                    adjusted['terrain'][key] *= 1.3
        
        # Adjustment 4: Climate-based adjustments
        climate = context.get('climate', 'semi_arid')
        if climate in ['arid', 'desert']:
            logger.debug("Arid climate - emphasizing water resources")
            if 'environment' in adjusted:
                if 'water_availability' in adjusted['environment']:
                    adjusted['environment']['water_availability'] *= 1.4
        
        # Normalize weights to sum to 1.0
        adjusted = self._normalize_weights(adjusted)
        
        return adjusted
    
    def _suggest_land_use(
        self,
        context: Dict,
        area_km2: float
    ) -> str:
        """
        Suggest primary land use based on context
        
        Returns:
            Suggested land use type
        """
        urbanization = context.get('urbanization_level') or context.get('estimated_urbanization', 'suburban')
        climate = context.get('climate', 'semi_arid')
        
        # Decision tree for land use suggestion
        if urbanization == 'urban':
            if area_km2 < 0.01:
                return 'residential'
            else:
                return 'mixed_use'
        
        elif urbanization == 'suburban':
            if area_km2 < 0.1:
                return 'residential'
            else:
                return 'commercial'
        
        elif urbanization == 'rural':
            if area_km2 > 0.5 and climate in ['mediterranean', 'semi_arid']:
                return 'agricultural'
            else:
                return 'residential'
        
        else:  # remote
            if area_km2 > 1.0:
                return 'agricultural'
            else:
                return 'residential'
    
    def _generate_reasoning(
        self,
        context: Dict,
        land_use_hint: str,
        criteria: Dict
    ) -> List[str]:
        """
        Generate human-readable reasoning for criteria selection
        
        Returns:
            List of reasoning statements
        """
        reasoning = []
        
        urbanization = context.get('urbanization_level') or context.get('estimated_urbanization', 'suburban')
        climate = context.get('climate', 'semi_arid')
        area_km2 = context.get('area_km2', 0)
        nearest_city_km = context.get('nearest_major_city_km', 50)
        
        # Urbanization reasoning
        reasoning.append(
            f"Location classified as '{urbanization}' "
            f"({nearest_city_km:.0f}km from nearest major city)"
        )
        
        # Climate reasoning
        reasoning.append(f"Climate zone: {climate.replace('_', ' ')}")
        
        # Area reasoning
        reasoning.append(f"Area size: {area_km2:.2f} km² ({context.get('size_class', 'unknown')})")
        
        # Criteria focus
        if 'accessibility' in criteria and sum(criteria['accessibility'].values()) > 0.2:
            reasoning.append("High emphasis on accessibility due to location characteristics")
        
        if 'terrain' in criteria:
            reasoning.append("Terrain suitability is key factor for buildability assessment")
        
        # Land use suggestion reasoning
        reasoning.append(f"Suggested primary land use: {land_use_hint}")
        
        return reasoning
    
    def _deep_copy_criteria(self, criteria: Dict) -> Dict:
        """Deep copy criteria dictionary"""
        import copy
        return copy.deepcopy(criteria)
    
    def _normalize_weights(self, criteria: Dict) -> Dict:
        """
        Normalize all weights to sum to 1.0
        
        Args:
            criteria: Nested criteria dictionary
            
        Returns:
            Normalized criteria dictionary
        """
        # Calculate total weight
        total = sum(
            sum(weights.values())
            for weights in criteria.values()
            if isinstance(weights, dict)
        )
        
        if total == 0:
            logger.warning("Total weight is 0, cannot normalize")
            return criteria
        
        # Normalize
        normalized = {}
        for category, weights in criteria.items():
            if isinstance(weights, dict):
                normalized[category] = {
                    key: value / total
                    for key, value in weights.items()
                }
            else:
                normalized[category] = weights
        
        return normalized
    
    def _flatten_criteria(self, criteria: Dict) -> Dict:
        """Flatten nested criteria into single dict"""
        flat = {}
        for category, weights in criteria.items():
            if isinstance(weights, dict):
                for criterion, weight in weights.items():
                    key = f"{category}_{criterion}"
                    flat[key] = weight
        return flat
    
    def _estimate_city_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Rough distance estimate in km"""
        import math
        
        lat_diff = abs(lat2 - lat1)
        lon_diff = abs(lon2 - lon1)
        
        # Very rough approximation
        km_per_deg = 111.32
        
        return math.sqrt(
            (lat_diff * km_per_deg) ** 2 +
            (lon_diff * km_per_deg * math.cos(math.radians(lat1))) ** 2
        )
