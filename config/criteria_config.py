# ============================================================================
# FILE: config/criteria_config.py (ENHANCED WITH NEW CRITERIA)
# ============================================================================

from typing import Dict, List
import yaml
from pathlib import Path

class CriteriaConfig:
    """Enhanced configuration for land evaluation criteria"""
    
    # ========== RESIDENTIAL DEVELOPMENT ==========
    RESIDENTIAL_CRITERIA = {
        'terrain': {
            'slope': 0.15,
            'elevation': 0.08,
            'aspect': 0.05
        },
        'accessibility': {
            'road_proximity': 0.12,
            'public_transport': 0.08,
            'motorway_access': 0.06
        },
        'urban_context': {
            'urban_proximity': 0.10,
            'population_density': 0.05,
            'development_pressure': 0.05
        },
        'amenities': {
            'schools': 0.08,
            'healthcare': 0.06,
            'shopping': 0.05,
            'parks': 0.04
        },
        'infrastructure': {
            'utilities_complete': 0.08,
            'internet_quality': 0.03
        },
        'environment': {
            'flood_risk': 0.08,
            'air_quality': 0.04,
            'noise_level': 0.03
        }
    }
    
    # ========== COMMERCIAL DEVELOPMENT ==========
    COMMERCIAL_CRITERIA = {
        'location': {
            'urban_centrality': 0.15,
            'visibility': 0.10,
            'traffic_flow': 0.12
        },
        'accessibility': {
            'road_access': 0.12,
            'parking_potential': 0.08,
            'public_transport': 0.06
        },
        'market': {
            'population_catchment': 0.10,
            'commercial_density': 0.08,
            'competition_level': 0.06
        },
        'infrastructure': {
            'utilities_complete': 0.08,
            'telecommunications': 0.05
        },
        'economic': {
            'market_growth': 0.08,
            'land_value_trend': 0.05,
            'economic_activity': 0.05
        },
        'zoning': {
            'commercial_zoning': 0.02
        }
    }
    
    # ========== AGRICULTURAL DEVELOPMENT ==========
    AGRICULTURAL_CRITERIA = {
        'soil': {
            'fertility': 0.20,
            'drainage': 0.12,
            'depth': 0.08
        },
        'water': {
            'irrigation_access': 0.15,
            'rainfall': 0.08,
            'groundwater': 0.06
        },
        'terrain': {
            'slope': 0.10,
            'aspect': 0.05
        },
        'climate': {
            'temperature_suitability': 0.06,
            'frost_risk': 0.04
        },
        'accessibility': {
            'market_access': 0.08,
            'road_quality': 0.06
        },
        'services': {
            'agricultural_support': 0.02
        }
    }
    
    # ========== INDUSTRIAL DEVELOPMENT ==========
    INDUSTRIAL_CRITERIA = {
        'location': {
            'industrial_zone_proximity': 0.12,
            'buffer_from_residential': 0.08
        },
        'transport': {
            'highway_access': 0.15,
            'rail_access': 0.10,
            'port_proximity': 0.08
        },
        'terrain': {
            'flatness': 0.12,
            'load_bearing_capacity': 0.08
        },
        'infrastructure': {
            'heavy_power_supply': 0.10,
            'water_supply': 0.06,
            'waste_management': 0.05
        },
        'workforce': {
            'labor_availability': 0.06,
            'housing_nearby': 0.04
        }
    }
    
    # ========== MIXED-USE DEVELOPMENT ==========
    MIXED_USE_CRITERIA = {
        'urban_context': {
            'urban_proximity': 0.12,
            'development_pressure': 0.08,
            'mixed_zoning': 0.06
        },
        'accessibility': {
            'multi_modal_access': 0.12,
            'pedestrian_friendly': 0.08,
            'cycling_infrastructure': 0.04
        },
        'amenities': {
            'diverse_services': 0.10,
            'cultural_facilities': 0.05
        },
        'infrastructure': {
            'complete_utilities': 0.10,
            'smart_infrastructure': 0.05
        },
        'economic': {
            'mixed_market_potential': 0.10,
            'job_housing_balance': 0.06
        },
        'environment': {
            'sustainability_potential': 0.04
        }
    }
    
    # ========== SCORING THRESHOLDS ==========
    THRESHOLDS = {
        'road_distance': {
            'excellent': (0, 200),
            'good': (200, 500),
            'moderate': (500, 1000),
            'poor': (1000, 2000),
            'unsuitable': (2000, 999999)
        },
        'urban_distance': {
            'city_center': (0, 2000),
            'urban': (2000, 5000),
            'suburban': (5000, 15000),
            'rural': (15000, 999999)
        },
        'population_density': {
            'very_high': (5000, 999999),
            'high': (2000, 5000),
            'medium': (500, 2000),
            'low': (100, 500),
            'very_low': (0, 100)
        },
        'public_transport_score': {
            'excellent': (8, 10),
            'good': (6, 8),
            'moderate': (4, 6),
            'poor': (2, 4),
            'very_poor': (0, 2)
        }
    }
    
    @classmethod
    def get_criteria_for_use(cls, land_use: str) -> Dict:
        """Get criteria weights for specific land use"""
        criteria_map = {
            'residential': cls.RESIDENTIAL_CRITERIA,
            'commercial': cls.COMMERCIAL_CRITERIA,
            'agricultural': cls.AGRICULTURAL_CRITERIA,
            'industrial': cls.INDUSTRIAL_CRITERIA,
            'mixed_use': cls.MIXED_USE_CRITERIA
        }
        return criteria_map.get(land_use.lower(), cls.RESIDENTIAL_CRITERIA)
    
    @classmethod
    def auto_select_criteria(cls, location_data: Dict) -> Dict:
        """
        Automatically select relevant criteria based on location
        """
        # Analyze location characteristics
        urban_level = location_data.get('urbanization_level', 'suburban')
        population = location_data.get('population_density', 500)
        
        # Select base criteria
        if urban_level in ['city_center', 'urban'] or population > 2000:
            base_criteria = cls.MIXED_USE_CRITERIA
        elif urban_level == 'suburban':
            base_criteria = cls.RESIDENTIAL_CRITERIA
        else:
            base_criteria = cls.AGRICULTURAL_CRITERIA
        
        # Adjust weights based on features
        return cls._adjust_criteria_weights(base_criteria, location_data)
    
    @classmethod
    def _adjust_criteria_weights(cls, base_criteria: Dict, features: Dict) -> Dict:
        """Dynamically adjust criteria weights based on features"""
        adjusted = base_criteria.copy()
        
        # Increase accessibility weight if remote
        if features.get('nearest_road_distance', 0) > 2000:
            if 'accessibility' in adjusted:
                for key in adjusted['accessibility']:
                    adjusted['accessibility'][key] *= 1.3
        
        # Increase infrastructure weight if utilities lacking
        utilities_count = sum([
            features.get('electricity_grid', False),
            features.get('water_network', False),
            features.get('sewage_system', False)
        ])
        if utilities_count < 3:
            if 'infrastructure' in adjusted:
                for key in adjusted['infrastructure']:
                    adjusted['infrastructure'][key] *= 1.2
        
        # Normalize weights to sum to 1.0
        return cls._normalize_weights(adjusted)
    
    @classmethod
    def _normalize_weights(cls, criteria: Dict) -> Dict:
        """Normalize all weights to sum to 1.0"""
        total = sum(
            sum(weights.values()) 
            for weights in criteria.values()
        )
        
        if total == 0:
            return criteria
        
        normalized = {}
        for category, weights in criteria.items():
            normalized[category] = {
                key: value / total 
                for key, value in weights.items()
            }
        
        return normalized
    
    @classmethod
    def flatten_criteria(cls, criteria: Dict) -> Dict:
        """Flatten nested criteria dictionary"""
        flat = {}
        for category, items in criteria.items():
            for criterion, weight in items.items():
                key = f"{category}_{criterion}"
                flat[key] = weight
        return flat
    
    @classmethod
    def get_criterion_score(cls, criterion_name: str, value: float, land_use: str = 'residential') -> float:
        """
        Score a specific criterion value (0-10 scale)
        """
        # Road distance scoring
        if 'road' in criterion_name and 'distance' in criterion_name:
            if value < 200:
                return 10.0
            elif value < 500:
                return 8.5
            elif value < 1000:
                return 7.0
            elif value < 2000:
                return 5.0
            elif value < 5000:
                return 3.0
            else:
                return 1.0
        
        # Urban proximity scoring
        elif 'urban' in criterion_name and 'proximity' in criterion_name:
            if land_use == 'commercial':
                # Closer is better for commercial
                if value < 2000:
                    return 10.0
                elif value < 5000:
                    return 8.0
                elif value < 10000:
                    return 6.0
                else:
                    return 3.0
            else:
                # Moderate distance is better for residential
                if 2000 < value < 10000:
                    return 9.0
                elif value < 2000:
                    return 7.0
                elif value < 20000:
                    return 6.0
                else:
                    return 4.0
        
        # Population density scoring
        elif 'population_density' in criterion_name:
            if land_use == 'commercial':
                # Higher is better for commercial
                if value > 5000:
                    return 10.0
                elif value > 2000:
                    return 8.0
                elif value > 500:
                    return 5.0
                else:
                    return 3.0
            elif land_use == 'agricultural':
                # Lower is better for agricultural
                if value < 100:
                    return 10.0
                elif value < 500:
                    return 7.0
                else:
                    return 3.0
            else:
                # Moderate is better for residential
                if 500 < value < 2000:
                    return 9.0
                elif value < 500:
                    return 7.0
                else:
                    return 5.0
        
        # Default linear scoring (0-10 scale)
        else:
            return min(10.0, max(0.0, value))
