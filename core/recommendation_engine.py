# ============================================================================
# FILE: core/recommendation_engine.py (COMPREHENSIVE VERSION)
# ============================================================================

from typing import Dict, List, Tuple
import numpy as np

class RecommendationEngine:
    """
    Generate detailed land use recommendations with sub-types
    Evaluates 40+ different land use possibilities
    """
    
    # Define all land use types with detailed sub-categories
    LAND_USE_TYPES = {
        'residential': {
            'single_family': {
                'name': 'Single-Family Homes',
                'description': 'Detached houses for individual families',
                'min_area_m2': 300,
                'ideal_slope': (0, 8),
                'urban_preference': 'suburban',
                'roi_potential': 'high'
            },
            'multi_family': {
                'name': 'Multi-Family Apartments',
                'description': 'Apartment buildings or condominiums',
                'min_area_m2': 1000,
                'ideal_slope': (0, 5),
                'urban_preference': 'urban',
                'roi_potential': 'very_high'
            },
            'luxury_villas': {
                'name': 'Luxury Villas',
                'description': 'High-end residential properties',
                'min_area_m2': 1000,
                'ideal_slope': (0, 15),
                'urban_preference': 'suburban',
                'roi_potential': 'very_high'
            },
            'social_housing': {
                'name': 'Social/Affordable Housing',
                'description': 'Government-supported affordable housing',
                'min_area_m2': 500,
                'ideal_slope': (0, 5),
                'urban_preference': 'urban',
                'roi_potential': 'medium'
            },
            'townhouses': {
                'name': 'Townhouses/Row Houses',
                'description': 'Connected multi-story homes',
                'min_area_m2': 200,
                'ideal_slope': (0, 8),
                'urban_preference': 'suburban',
                'roi_potential': 'high'
            },
            'retirement_community': {
                'name': 'Retirement Community',
                'description': 'Housing for senior citizens',
                'min_area_m2': 2000,
                'ideal_slope': (0, 3),
                'urban_preference': 'suburban',
                'roi_potential': 'medium'
            },
            'student_housing': {
                'name': 'Student Housing',
                'description': 'Dormitories or student apartments',
                'min_area_m2': 500,
                'ideal_slope': (0, 5),
                'urban_preference': 'urban',
                'roi_potential': 'high'
            },
            'mixed_residential': {
                'name': 'Mixed Residential',
                'description': 'Combination of housing types',
                'min_area_m2': 2000,
                'ideal_slope': (0, 10),
                'urban_preference': 'suburban',
                'roi_potential': 'high'
            }
        },
        
        'commercial': {
            'retail': {
                'name': 'Retail Shopping',
                'description': 'Stores and retail outlets',
                'min_area_m2': 500,
                'ideal_slope': (0, 3),
                'urban_preference': 'urban',
                'roi_potential': 'very_high'
            },
            'offices': {
                'name': 'Office Buildings',
                'description': 'Professional office space',
                'min_area_m2': 1000,
                'ideal_slope': (0, 5),
                'urban_preference': 'urban',
                'roi_potential': 'high'
            },
            'shopping_mall': {
                'name': 'Shopping Mall/Center',
                'description': 'Large retail complex',
                'min_area_m2': 10000,
                'ideal_slope': (0, 3),
                'urban_preference': 'urban',
                'roi_potential': 'very_high'
            },
            'restaurant': {
                'name': 'Restaurant/Cafe Complex',
                'description': 'Food service establishments',
                'min_area_m2': 300,
                'ideal_slope': (0, 5),
                'urban_preference': 'urban',
                'roi_potential': 'high'
            },
            'hotel': {
                'name': 'Hotel/Hospitality',
                'description': 'Accommodation facilities',
                'min_area_m2': 2000,
                'ideal_slope': (0, 10),
                'urban_preference': 'suburban',
                'roi_potential': 'high'
            },
            'gas_station': {
                'name': 'Gas Station/Service Center',
                'description': 'Fuel and vehicle services',
                'min_area_m2': 500,
                'ideal_slope': (0, 3),
                'urban_preference': 'any',
                'roi_potential': 'medium'
            },
            'mixed_commercial': {
                'name': 'Mixed Commercial',
                'description': 'Multiple commercial uses',
                'min_area_m2': 2000,
                'ideal_slope': (0, 5),
                'urban_preference': 'urban',
                'roi_potential': 'very_high'
            }
        },
        
        'agricultural': {
            'cereals': {
                'name': 'Cereal Crops (Wheat, Barley)',
                'description': 'Large-scale grain farming',
                'min_area_m2': 10000,
                'ideal_slope': (0, 8),
                'urban_preference': 'rural',
                'roi_potential': 'medium'
            },
            'vegetables': {
                'name': 'Vegetables/Horticulture',
                'description': 'Intensive vegetable production',
                'min_area_m2': 2000,
                'ideal_slope': (0, 5),
                'urban_preference': 'rural',
                'roi_potential': 'high'
            },
            'orchards': {
                'name': 'Orchards (Fruits, Olives)',
                'description': 'Tree fruit cultivation',
                'min_area_m2': 5000,
                'ideal_slope': (0, 15),
                'urban_preference': 'rural',
                'roi_potential': 'high'
            },
            'vineyards': {
                'name': 'Vineyards',
                'description': 'Grape cultivation for wine',
                'min_area_m2': 5000,
                'ideal_slope': (3, 20),
                'urban_preference': 'rural',
                'roi_potential': 'very_high'
            },
            'livestock': {
                'name': 'Livestock (Cattle, Sheep)',
                'description': 'Animal grazing and farming',
                'min_area_m2': 20000,
                'ideal_slope': (0, 15),
                'urban_preference': 'rural',
                'roi_potential': 'medium'
            },
            'poultry': {
                'name': 'Poultry Farming',
                'description': 'Chicken, egg production',
                'min_area_m2': 2000,
                'ideal_slope': (0, 5),
                'urban_preference': 'rural',
                'roi_potential': 'high'
            },
            'greenhouse': {
                'name': 'Greenhouse Farming',
                'description': 'Controlled environment agriculture',
                'min_area_m2': 1000,
                'ideal_slope': (0, 5),
                'urban_preference': 'rural',
                'roi_potential': 'very_high'
            },
            'organic': {
                'name': 'Organic Farming',
                'description': 'Certified organic production',
                'min_area_m2': 5000,
                'ideal_slope': (0, 10),
                'urban_preference': 'rural',
                'roi_potential': 'high'
            }
        },
        
        'industrial': {
            'light_manufacturing': {
                'name': 'Light Manufacturing',
                'description': 'Small-scale production facilities',
                'min_area_m2': 2000,
                'ideal_slope': (0, 3),
                'urban_preference': 'suburban',
                'roi_potential': 'high'
            },
            'heavy_industry': {
                'name': 'Heavy Industry',
                'description': 'Large-scale industrial production',
                'min_area_m2': 10000,
                'ideal_slope': (0, 5),
                'urban_preference': 'rural',
                'roi_potential': 'very_high'
            },
            'warehouse': {
                'name': 'Warehouse/Logistics',
                'description': 'Storage and distribution',
                'min_area_m2': 5000,
                'ideal_slope': (0, 3),
                'urban_preference': 'suburban',
                'roi_potential': 'high'
            },
            'food_processing': {
                'name': 'Food Processing Plant',
                'description': 'Agricultural product processing',
                'min_area_m2': 3000,
                'ideal_slope': (0, 3),
                'urban_preference': 'rural',
                'roi_potential': 'high'
            },
            'tech_park': {
                'name': 'Technology/Business Park',
                'description': 'Modern tech facilities',
                'min_area_m2': 5000,
                'ideal_slope': (0, 5),
                'urban_preference': 'suburban',
                'roi_potential': 'very_high'
            },
            'workshops': {
                'name': 'Craft Workshops',
                'description': 'Artisan production spaces',
                'min_area_m2': 500,
                'ideal_slope': (0, 5),
                'urban_preference': 'any',
                'roi_potential': 'medium'
            }
        },
        
        'tourism': {
            'eco_resort': {
                'name': 'Eco-Tourism Resort',
                'description': 'Sustainable tourism facility',
                'min_area_m2': 10000,
                'ideal_slope': (0, 20),
                'urban_preference': 'rural',
                'roi_potential': 'very_high'
            },
            'adventure_park': {
                'name': 'Adventure/Theme Park',
                'description': 'Recreational entertainment',
                'min_area_m2': 20000,
                'ideal_slope': (0, 15),
                'urban_preference': 'suburban',
                'roi_potential': 'high'
            },
            'camping': {
                'name': 'Camping/Glamping Site',
                'description': 'Outdoor accommodation',
                'min_area_m2': 5000,
                'ideal_slope': (0, 15),
                'urban_preference': 'rural',
                'roi_potential': 'medium'
            },
            'sports_complex': {
                'name': 'Sports Complex',
                'description': 'Athletic facilities',
                'min_area_m2': 10000,
                'ideal_slope': (0, 5),
                'urban_preference': 'suburban',
                'roi_potential': 'medium'
            },
            'cultural_center': {
                'name': 'Cultural/Event Center',
                'description': 'Cultural activities venue',
                'min_area_m2': 2000,
                'ideal_slope': (0, 5),
                'urban_preference': 'urban',
                'roi_potential': 'medium'
            }
        },
        
        'energy': {
            'solar_farm': {
                'name': 'Solar Farm',
                'description': 'Photovoltaic energy generation',
                'min_area_m2': 10000,
                'ideal_slope': (0, 10),
                'urban_preference': 'rural',
                'roi_potential': 'high'
            },
            'wind_farm': {
                'name': 'Wind Farm',
                'description': 'Wind turbine energy',
                'min_area_m2': 50000,
                'ideal_slope': (0, 20),
                'urban_preference': 'rural',
                'roi_potential': 'high'
            },
            'biomass': {
                'name': 'Biomass Energy Plant',
                'description': 'Renewable organic energy',
                'min_area_m2': 5000,
                'ideal_slope': (0, 5),
                'urban_preference': 'rural',
                'roi_potential': 'medium'
            },
            'energy_storage': {
                'name': 'Energy Storage Facility',
                'description': 'Battery/storage systems',
                'min_area_m2': 2000,
                'ideal_slope': (0, 3),
                'urban_preference': 'any',
                'roi_potential': 'high'
            }
        }
    }
    
    def generate_recommendations(
        self,
        features: Dict,
        scores: Dict,
        criteria: Dict,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Generate comprehensive recommendations for all land use types
        Returns top N recommendations ranked by suitability
        """
        
        all_recommendations = []
        
        # Evaluate each category and sub-type
        for category, subtypes in self.LAND_USE_TYPES.items():
            for subtype_key, subtype_info in subtypes.items():
                
                # Calculate suitability for this specific use
                suitability = self._calculate_suitability(
                    category,
                    subtype_key,
                    subtype_info,
                    features,
                    scores
                )
                
                # Only include if suitability score is reasonable
                if suitability['score'] >= 4.0:
                    all_recommendations.append({
                        'rank': 0,  # Will be assigned after sorting
                        'category': category,
                        'subtype': subtype_key,
                        'usage_type': subtype_info['name'],
                        'description': subtype_info['description'],
                        'suitability_score': suitability['score'],
                        'confidence': suitability['confidence'],
                        'supporting_factors': suitability['factors'],
                        'concerns': suitability['concerns'],
                        'estimated_roi': suitability['roi'],
                        'development_cost': suitability['development_cost'],
                        'time_to_market': suitability['time_to_market'],
                        'market_demand': suitability['market_demand']
                    })
        
        # Sort by suitability score
        all_recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        # Assign ranks
        for i, rec in enumerate(all_recommendations):
            rec['rank'] = i + 1
        
        # Return top N
        return all_recommendations[:top_n]
    
    def _calculate_suitability(
        self,
        category: str,
        subtype: str,
        subtype_info: Dict,
        features: Dict,
        scores: Dict
    ) -> Dict:
        """
        Calculate detailed suitability score for a specific land use type
        """
        
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        boundary = features.get('boundary', {})
        
        # Base score
        score = 5.0
        factors = []
        concerns = []
        
        # ========== AREA CHECK ==========
        area_m2 = boundary.get('area_m2', 0)
        min_area = subtype_info['min_area_m2']
        
        if area_m2 < min_area:
            score -= 3.0
            concerns.append(f"Area too small: {area_m2:.0f}m² (minimum: {min_area:.0f}m²)")
        elif area_m2 > min_area * 3:
            score += 1.0
            factors.append(f"Excellent area: {area_m2/10000:.2f} hectares")
        
        # ========== SLOPE CHECK ==========
        slope = terrain.get('slope_avg', 999)
        ideal_slope_min, ideal_slope_max = subtype_info['ideal_slope']
        
        if ideal_slope_min <= slope <= ideal_slope_max:
            score += 2.0
            factors.append(f"Ideal slope: {slope:.1f}° (perfect for this use)")
        elif slope < ideal_slope_min - 2 or slope > ideal_slope_max + 5:
            score -= 1.5
            concerns.append(f"Slope {slope:.1f}° not ideal (prefer {ideal_slope_min}-{ideal_slope_max}°)")
        
        # ========== URBAN CONTEXT ==========
        urban_level = infra.get('urbanization_level', 'unknown')
        preferred_urban = subtype_info['urban_preference']
        
        urban_match_scores = {
            ('urban', 'urban'): 2.5,
            ('suburban', 'suburban'): 2.5,
            ('rural', 'rural'): 2.5,
            ('urban', 'suburban'): 1.5,
            ('suburban', 'urban'): 1.5,
            ('suburban', 'rural'): 1.0,
            ('rural', 'suburban'): 1.0,
            ('any', 'urban'): 1.5,
            ('any', 'suburban'): 1.5,
            ('any', 'rural'): 1.5
        }
        
        match_key = (preferred_urban, urban_level)
        match_score = urban_match_scores.get(match_key, 0)
        score += match_score
        
        if match_score >= 2.0:
            factors.append(f"Perfect location: {urban_level} area matches {preferred_urban} preference")
        elif match_score < 1.0:
            concerns.append(f"Location mismatch: {urban_level} area, prefers {preferred_urban}")
        
        # ========== CATEGORY-SPECIFIC SCORING ==========
        
        if category == 'residential':
            score += self._score_residential(subtype, features, factors, concerns)
        
        elif category == 'commercial':
            score += self._score_commercial(subtype, features, factors, concerns)
        
        elif category == 'agricultural':
            score += self._score_agricultural(subtype, features, factors, concerns)
        
        elif category == 'industrial':
            score += self._score_industrial(subtype, features, factors, concerns)
        
        elif category == 'tourism':
            score += self._score_tourism(subtype, features, factors, concerns)
        
        elif category == 'energy':
            score += self._score_energy(subtype, features, factors, concerns)
        
        # ========== FINAL ADJUSTMENTS ==========
        
        # Limit score to 0-10 range
        final_score = max(0, min(10, score))
        
        # Calculate other metrics
        confidence = self._calculate_confidence(features, final_score)
        roi = self._estimate_roi(category, subtype, final_score, subtype_info['roi_potential'])
        dev_cost = self._estimate_development_cost(category, subtype, area_m2)
        time_to_market = self._estimate_time_to_market(category, subtype)
        market_demand = self._estimate_market_demand(category, subtype, infra)
        
        return {
            'score': round(final_score, 2),
            'confidence': confidence,
            'factors': factors,
            'concerns': concerns,
            'roi': roi,
            'development_cost': dev_cost,
            'time_to_market': time_to_market,
            'market_demand': market_demand
        }
    
    # Continue in next message...
