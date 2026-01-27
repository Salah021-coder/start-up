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

# ============================================================================
# Continuing: core/recommendation_engine.py
# Category-specific scoring methods
# ============================================================================

    def _score_residential(self, subtype: str, features: Dict, factors: List, concerns: List) -> float:
        """Score residential developments"""
        score = 0.0
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        # Infrastructure access (critical for residential)
        road_dist = infra.get('nearest_road_distance', 999999)
        if road_dist < 500:
            score += 2.0
            factors.append(f"Excellent road access: {road_dist:.0f}m")
        elif road_dist > 2000:
            score -= 1.5
            concerns.append(f"Limited road access: {road_dist/1000:.1f}km")
        
        # Amenities (schools, healthcare, shopping)
        schools = infra.get('schools_count_3km', 0)
        hospitals = infra.get('hospitals_count_5km', 0)
        shops = infra.get('supermarkets_count_2km', 0)
        
        if schools >= 3 and hospitals >= 1 and shops >= 2:
            score += 2.5
            factors.append(f"Rich amenities: {schools} schools, {hospitals} hospitals, {shops} supermarkets")
        elif schools < 1 or hospitals < 1:
            score -= 1.0
            concerns.append("Limited amenities nearby")
        
        # Utilities (essential for residential)
        utilities_count = sum([
            infra.get('electricity_grid', False),
            infra.get('water_network', False),
            infra.get('sewage_system', False)
        ])
        
        if utilities_count == 3:
            score += 1.5
            factors.append("All essential utilities available")
        elif utilities_count < 2:
            score -= 2.0
            concerns.append(f"Missing utilities: only {utilities_count}/3 available")
        
        # Environmental quality
        flood_risk = env.get('flood_risk_percent', 0)
        if flood_risk < 10:
            score += 1.0
            factors.append("Low flood risk")
        elif flood_risk > 30:
            score -= 2.0
            concerns.append(f"High flood risk: {flood_risk:.0f}% of area")
        
        # Public transport (bonus for urban residential)
        if subtype in ['multi_family', 'student_housing', 'social_housing']:
            transport_score = infra.get('public_transport_score', 0)
            if transport_score > 7:
                score += 1.5
                factors.append(f"Excellent public transport: {transport_score:.1f}/10")
        
        # Luxury villa specific
        if subtype == 'luxury_villas':
            # Views and privacy are important
            elevation = terrain.get('elevation_avg', 0)
            if elevation > 200:
                score += 1.0
                factors.append("Elevated position - good views potential")
            
            # Prefer some distance from urban center
            urban_dist = infra.get('nearest_city_distance', 0)
            if 5000 < urban_dist < 20000:
                score += 0.5
                factors.append("Ideal distance from city - privacy with access")
        
        return score
    
    def _score_commercial(self, subtype: str, features: Dict, factors: List, concerns: List) -> float:
        """Score commercial developments"""
        score = 0.0
        infra = features.get('infrastructure', {})
        
        # Population density (critical for commercial)
        pop_density = infra.get('population_density', 0)
        if pop_density > 2000:
            score += 2.5
            factors.append(f"High population density: {pop_density:.0f}/km²")
        elif pop_density < 500:
            score -= 2.0
            concerns.append(f"Low population density: {pop_density:.0f}/km² - limited market")
        
        # Visibility and traffic
        road_type = infra.get('road_type', 'unknown')
        if road_type in ['primary', 'secondary', 'motorway']:
            score += 2.0
            factors.append(f"High visibility: Located on {road_type} road")
        
        # Urban centrality
        urban_level = infra.get('urbanization_level', 'rural')
        if urban_level in ['urban', 'city_center']:
            score += 2.0
            factors.append("Prime urban location")
        
        # Specific commercial types
        if subtype == 'shopping_mall':
            # Needs large area and excellent access
            motorway = infra.get('motorway_distance', 999999)
            if motorway < 5000:
                score += 1.5
                factors.append(f"Motorway access: {motorway/1000:.1f}km")
            
            total_amenities = infra.get('total_amenities', 0)
            if total_amenities > 30:
                score += 1.0
                factors.append("Established commercial area")
        
        elif subtype == 'restaurant':
            # Foot traffic important
            bus_stops = infra.get('bus_stops_count_1km', 0)
            if bus_stops > 3:
                score += 1.0
                factors.append(f"Good foot traffic: {bus_stops} bus stops nearby")
        
        elif subtype == 'hotel':
            # Tourism potential
            restaurants = infra.get('restaurants_count_1km', 0)
            if restaurants > 5:
                score += 1.0
                factors.append("Active hospitality area")
        
        # Development pressure (indicates commercial viability)
        dev_pressure = infra.get('development_pressure', 'low')
        if dev_pressure == 'high':
            score += 1.5
            factors.append("High development activity - strong market")
        
        return score
    
    def _score_agricultural(self, subtype: str, features: Dict, factors: List, concerns: List) -> float:
        """Score agricultural uses"""
        score = 0.0
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        # Soil quality (from NDVI as proxy)
        ndvi = env.get('ndvi_avg', 0)
        if ndvi > 0.6:
            score += 2.5
            factors.append(f"Excellent vegetation index: NDVI {ndvi:.2f}")
        elif ndvi < 0.3:
            score -= 1.5
            concerns.append(f"Poor vegetation: NDVI {ndvi:.2f}")
        
        # Water availability
        water_occurrence = env.get('water_occurrence_avg', 0)
        if water_occurrence > 20:
            score += 1.5
            factors.append("Good water availability")
        elif water_occurrence < 5:
            concerns.append("Limited water resources - irrigation may be needed")
        
        # Market access (roads important even for agriculture)
        road_dist = infra.get('nearest_road_distance', 999999)
        if road_dist < 2000:
            score += 1.0
            factors.append("Good market access via roads")
        elif road_dist > 5000:
            score -= 1.0
            concerns.append("Remote location - transport costs will be high")
        
        # Specific agricultural types
        if subtype == 'cereals':
            # Prefer larger, flatter areas
            slope = terrain.get('slope_avg', 999)
            if slope < 5:
                score += 1.5
                factors.append("Flat terrain ideal for mechanized farming")
        
        elif subtype == 'orchards' or subtype == 'vineyards':
            # Can handle more slope, good drainage
            slope = terrain.get('slope_avg', 0)
            if 3 < slope < 15:
                score += 1.5
                factors.append(f"Slope {slope:.1f}° provides natural drainage")
        
        elif subtype == 'greenhouse':
            # Needs utilities
            electricity = infra.get('electricity_grid', False)
            water = infra.get('water_network', False)
            if electricity and water:
                score += 2.0
                factors.append("Utilities available for greenhouse operations")
        
        elif subtype == 'livestock':
            # Needs large area
            area = features.get('boundary', {}).get('area_hectares', 0)
            if area > 5:
                score += 1.5
                factors.append(f"Large area: {area:.1f} hectares suitable for grazing")
        
        # Climate suitability (Algeria-specific)
        elevation = terrain.get('elevation_avg', 0)
        if 500 < elevation < 1500:
            score += 1.0
            factors.append("Moderate elevation - good growing conditions")
        
        return score
    
    def _score_industrial(self, subtype: str, features: Dict, factors: List, concerns: List) -> float:
        """Score industrial developments"""
        score = 0.0
        terrain = features.get('terrain', {})
        infra = features.get('infrastructure', {})
        
        # Flat terrain essential
        slope = terrain.get('slope_avg', 999)
        if slope < 3:
            score += 2.5
            factors.append(f"Very flat terrain: {slope:.1f}° - ideal for industrial")
        elif slope > 8:
            score -= 2.0
            concerns.append(f"Too steep: {slope:.1f}° - expensive site preparation")
        
        # Heavy transport access
        motorway = infra.get('motorway_distance', 999999)
        primary_road = infra.get('primary_road_distance', 999999)
        
        if motorway < 10000 or primary_road < 3000:
            score += 2.0
            factors.append("Excellent logistics access")
        
        # Power supply critical
        electricity = infra.get('electricity_grid', False)
        if electricity:
            score += 1.5
            factors.append("Power grid available")
        else:
            score -= 2.5
            concerns.append("No electricity grid - major infrastructure needed")
        
        # Buffer from residential
        urban_dist = infra.get('nearest_city_distance', 0)
        if 5000 < urban_dist < 20000:
            score += 1.0
            factors.append("Safe distance from residential areas")
        elif urban_dist < 2000:
            concerns.append("Too close to residential - potential conflicts")
        
        # Specific industrial types
        if subtype == 'tech_park':
            # Needs good connectivity
            internet = infra.get('internet_fiber', False)
            if internet:
                score += 1.5
                factors.append("Fiber internet available")
        
        elif subtype == 'food_processing':
            # Proximity to agricultural areas
            ndvi = features.get('environmental', {}).get('ndvi_avg', 0)
            if ndvi > 0.4:
                score += 1.0
                factors.append("Located in agricultural region")
        
        return score
    
    def _score_tourism(self, subtype: str, features: Dict, factors: List, concerns: List) -> float:
        """Score tourism and recreation"""
        score = 0.0
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        # Natural beauty (NDVI as proxy)
        ndvi = env.get('ndvi_avg', 0)
        if ndvi > 0.5:
            score += 2.0
            factors.append("Beautiful natural environment")
        
        # Scenic value (elevation variation)
        elevation_range = terrain.get('elevation_max', 0) - terrain.get('elevation_min', 0)
        if elevation_range > 50:
            score += 1.5
            factors.append("Varied terrain - scenic potential")
        
        # Accessibility (still needs roads)
        road_dist = infra.get('nearest_road_distance', 999999)
        if road_dist < 1000:
            score += 1.5
            factors.append("Accessible for tourists")
        elif road_dist > 5000:
            score -= 1.5
            concerns.append("Too remote - access challenges")
        
        # Distance from urban (tourism often benefits from some isolation)
        urban_dist = infra.get('nearest_city_distance', 0)
        if 10000 < urban_dist < 50000:
            score += 1.5
            factors.append("Perfect distance - escape from city, still accessible")
        
        # Specific tourism types
        if subtype == 'eco_resort':
            # Environmental quality critical
            flood_risk = env.get('flood_risk_percent', 0)
            if flood_risk < 10:
                score += 1.0
                factors.append("Low environmental risks")
        
        elif subtype == 'sports_complex':
            # Needs flat area
            slope = terrain.get('slope_avg', 999)
            if slope < 5:
                score += 1.5
                factors.append("Flat terrain for sports facilities")
        
        return score
    
    def _score_energy(self, subtype: str, features: Dict, factors: List, concerns: List) -> float:
        """Score renewable energy projects"""
        score = 0.0
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        boundary = features.get('boundary', {})
        
        # Large area generally good for energy
        area = boundary.get('area_hectares', 0)
        if area > 5:
            score += 2.0
            factors.append(f"Large area: {area:.1f} hectares")
        
        # Grid connection important
        electricity = infra.get('electricity_grid', False)
        if electricity:
            score += 1.5
            factors.append("Power grid nearby for connection")
        
        # Specific energy types
        if subtype == 'solar_farm':
            # Southern exposure ideal
            aspect = terrain.get('aspect_direction', 'N')
            if aspect in ['S', 'SE', 'SW']:
                score += 2.0
                factors.append(f"Excellent solar exposure: {aspect} facing")
            
            # Flat or gentle slope
            slope = terrain.get('slope_avg', 999)
            if slope < 10:
                score += 1.0
                factors.append("Good slope for solar panels")
        
        elif subtype == 'wind_farm':
            # Elevated, open areas
            elevation = terrain.get('elevation_avg', 0)
            if elevation > 300:
                score += 1.5
                factors.append("Elevated position - good wind potential")
            
            # Sparse development
            pop_density = infra.get('population_density', 0)
            if pop_density < 100:
                score += 1.0
                factors.append("Low population - minimal noise complaints")
        
        # Environmental considerations
        flood_risk = env.get('flood_risk_percent', 0)
        if flood_risk < 10:
            score += 0.5
        
        return score
    
    def _calculate_confidence(self, features: Dict, score: float) -> float:
        """Calculate confidence in the recommendation"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence if data quality is good
        data_quality = features.get('infrastructure', {}).get('data_quality', 'unknown')
        if data_quality == 'real_osm':
            confidence += 0.15
        elif data_quality == 'enhanced':
            confidence += 0.10
        
        # Higher confidence for extreme scores (very suitable or unsuitable)
        if score > 8 or score < 3:
            confidence += 0.10
        
        return min(1.0, confidence)
    
    def _estimate_roi(self, category: str, subtype: str, score: float, roi_potential: str) -> str:
        """Estimate Return on Investment category"""
        
        roi_map = {
            'very_high': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        base_roi = roi_map.get(roi_potential, 2)
        
        # Adjust based on suitability score
        if score > 8:
            adjusted_roi = min(4, base_roi + 1)
        elif score < 5:
            adjusted_roi = max(1, base_roi - 1)
        else:
            adjusted_roi = base_roi
        
        roi_names = {4: 'Very High', 3: 'High', 2: 'Medium', 1: 'Low'}
        return roi_names.get(adjusted_roi, 'Medium')
    
    def _estimate_development_cost(self, category: str, subtype: str, area_m2: float) -> str:
        """Estimate development cost category"""
        
        # Base costs per category (relative)
        base_costs = {
            'residential': 2,
            'commercial': 3,
            'agricultural': 1,
            'industrial': 3,
            'tourism': 2,
            'energy': 3
        }
        
        base = base_costs.get(category, 2)
        
        # Adjust for area
        if area_m2 > 50000:
            base += 1
        elif area_m2 < 5000:
            base -= 1
        
        cost_names = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Very High'}
        return cost_names.get(max(1, min(4, base)), 'Medium')
    
    def _estimate_time_to_market(self, category: str, subtype: str) -> str:
        """Estimate time to develop and bring to market"""
        
        time_map = {
            'residential': {
                'single_family': '12-18 months',
                'multi_family': '18-24 months',
                'luxury_villas': '18-30 months',
                'social_housing': '12-18 months',
                'townhouses': '12-18 months',
                'retirement_community': '24-36 months',
                'student_housing': '12-18 months',
                'mixed_residential': '18-30 months'
            },
            'commercial': {
                'retail': '6-12 months',
                'offices': '12-18 months',
                'shopping_mall': '24-36 months',
                'restaurant': '3-6 months',
                'hotel': '18-24 months',
                'gas_station': '6-9 months',
                'mixed_commercial': '18-24 months'
            },
            'agricultural': {
                'cereals': '1-2 years (first harvest)',
                'vegetables': '3-6 months',
                'orchards': '3-5 years (maturity)',
                'vineyards': '3-5 years (maturity)',
                'livestock': '1-2 years',
                'poultry': '6-12 months',
                'greenhouse': '6-12 months',
                'organic': '2-3 years (certification)'
            },
            'industrial': {
                'light_manufacturing': '12-18 months',
                'heavy_industry': '24-36 months',
                'warehouse': '9-12 months',
                'food_processing': '12-18 months',
                'tech_park': '18-24 months',
                'workshops': '6-9 months'
            },
            'tourism': {
                'eco_resort': '18-30 months',
                'adventure_park': '18-24 months',
                'camping': '6-12 months',
                'sports_complex': '12-18 months',
                'cultural_center': '12-18 months'
            },
            'energy': {
                'solar_farm': '9-15 months',
                'wind_farm': '18-24 months',
                'biomass': '18-24 months',
                'energy_storage': '12-18 months'
            }
        }
        
        return time_map.get(category, {}).get(subtype, '12-18 months')
    
    def _estimate_market_demand(self, category: str, subtype: str, infra: Dict) -> str:
        """Estimate current market demand"""
        
        pop_density = infra.get('population_density', 0)
        urban_level = infra.get('urbanization_level', 'rural')
        dev_pressure = infra.get('development_pressure', 'low')
        
        # High demand indicators
        high_demand_conditions = (
            (pop_density > 2000) or
            (urban_level == 'urban') or
            (dev_pressure == 'high')
        )
        
        # Category-specific demand
        if category == 'residential':
            if high_demand_conditions:
                return 'Very High'
            elif pop_density > 500:
                return 'High'
            else:
                return 'Medium'
        
        elif category == 'commercial':
            if pop_density > 3000:
                return 'Very High'
            elif pop_density > 1000:
                return 'High'
            else:
                return 'Medium'
        
        elif category == 'agricultural':
            # Agricultural demand more stable
            return 'Medium'
        
        elif category == 'industrial':
            if dev_pressure == 'high':
                return 'High'
            else:
                return 'Medium'
        
        elif category in ['tourism', 'energy']:
            # Growing markets
            return 'High'
        
        return 'Medium'
