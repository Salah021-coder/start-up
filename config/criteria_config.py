from typing import Dict, List
import yaml
from pathlib import Path

class CriteriaConfig:
    """Configuration for land evaluation criteria"""
    
    # Default criteria weights for different land uses
    RESIDENTIAL_CRITERIA = {
        'terrain': {
            'slope': 0.25,
            'elevation': 0.15,
            'aspect': 0.10
        },
        'infrastructure': {
            'road_proximity': 0.20,
            'public_transport': 0.10
        },
        'environmental': {
            'flood_risk': 0.15,
            'air_quality': 0.05
        },
        'utilities': {
            'water_access': 0.10,
            'electricity': 0.10,
            'sewage': 0.05
        }
    }
    
    AGRICULTURAL_CRITERIA = {
        'soil': {
            'fertility': 0.30,
            'drainage': 0.20,
            'depth': 0.10
        },
        'water': {
            'irrigation_potential': 0.25,
            'rainfall': 0.10
        },
        'terrain': {
            'slope': 0.15,
            'aspect': 0.05
        },
        'climate': {
            'temperature': 0.05,
            'frost_risk': 0.05
        }
    }
    
    COMMERCIAL_CRITERIA = {
        'infrastructure': {
            'road_access': 0.25,
            'population_density': 0.20,
            'parking': 0.10
        },
        'economic': {
            'market_value': 0.20,
            'competition': 0.10
        },
        'utilities': {
            'all_utilities': 0.20
        },
        'visibility': {
            'traffic_flow': 0.15,
            'signage': 0.05
        }
    }
    
    INDUSTRIAL_CRITERIA = {
        'infrastructure': {
            'road_access': 0.30,
            'rail_access': 0.15,
            'port_proximity': 0.10
        },
        'terrain': {
            'flatness': 0.20,
            'load_bearing': 0.10
        },
        'utilities': {
            'power_capacity': 0.15,
            'water_supply': 0.10
        },
        'environmental': {
            'buffer_zones': 0.05,
            'emissions': 0.05
        }
    }
    
    # Scoring thresholds
    SLOPE_THRESHOLDS = {
        'excellent': (0, 3),      # 0-3 degrees
        'good': (3, 8),           # 3-8 degrees
        'moderate': (8, 15),      # 8-15 degrees
        'poor': (15, 30),         # 15-30 degrees
        'unsuitable': (30, 90)    # >30 degrees
    }
    
    FLOOD_RISK_THRESHOLDS = {
        'low': (0, 10),           # 0-10% probability
        'medium': (10, 30),       # 10-30% probability
        'high': (30, 100)         # >30% probability
    }
    
    ROAD_DISTANCE_THRESHOLDS = {
        'excellent': (0, 500),     # 0-500m
        'good': (500, 1000),       # 500-1000m
        'moderate': (1000, 2000),  # 1-2km
        'poor': (2000, 5000),      # 2-5km
        'unsuitable': (5000, 999999)  # >5km
    }
    
    @classmethod
    def get_criteria_for_use(cls, land_use: str) -> Dict:
        """Get criteria weights for specific land use"""
        criteria_map = {
            'residential': cls.RESIDENTIAL_CRITERIA,
            'agricultural': cls.AGRICULTURAL_CRITERIA,
            'commercial': cls.COMMERCIAL_CRITERIA,
            'industrial': cls.INDUSTRIAL_CRITERIA
        }
        return criteria_map.get(land_use.lower(), cls.RESIDENTIAL_CRITERIA)
    
    @classmethod
    def auto_select_criteria(cls, location_data: Dict) -> Dict:
        """
        Automatically select relevant criteria based on location characteristics
        """
        # This will be implemented with actual location analysis
        # For now, return default residential criteria
        return cls.RESIDENTIAL_CRITERIA
    
    @classmethod
    def flatten_criteria(cls, criteria: Dict) -> Dict:
        """Flatten nested criteria dictionary"""
        flat = {}
        for category, items in criteria.items():
            for criterion, weight in items.items():
                key = f"{category}_{criterion}"
                flat[key] = weight
        return flat