# ============================================================================
# FILE: core/recommendation/usage_recommender.py
# Land-Use Recommendation Engine
# ============================================================================

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class UsageRecommender:
    """
    Generate land-use recommendations
    
    RESPONSIBILITIES:
    - Evaluate suitability for different land uses
    - Consider risk factors
    - Rank recommendations
    - Provide supporting factors and concerns
    
    DOES NOT:
    - Extract features
    - Calculate base suitability
    - Assess risks directly
    """
    
    def __init__(self):
        """Initialize usage recommender"""
        
        # Land use types to evaluate
        self.land_use_types = [
            'residential_individual',
            'residential_collective',
            'residential_mixed',
            'commercial_retail',
            'commercial_office',
            'industrial_light',
            'industrial_heavy',
            'agricultural_crops',
            'agricultural_orchards',
            'agricultural_livestock',
            'tourism_hotel',
            'tourism_recreation',
            'mixed_use',
            'solar_farm',
            'logistics_warehouse'
        ]
    
    def generate_recommendations(
        self,
        features: Dict,
        risk_result,
        suitability_scores: Dict,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Generate ranked land-use recommendations
        
        Args:
            features: Extracted features
            risk_result: Risk assessment result
            suitability_scores: AHP suitability scores
            top_n: Number of recommendations to return
            
        Returns:
            List of recommendation dicts, sorted by suitability
        """
        logger.info(f"Generating top {top_n} land-use recommendations")
        
        # Extract context
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        boundary = features.get('boundary', {})
        
        area_km2 = boundary.get('area_km2', 0)
        
        # Base suitability from AHP
        base_suitability = suitability_scores.get('overall_score', 5.0)
        
        # Evaluate each land use
        evaluations = []
        
        for land_use in self.land_use_types:
            evaluation = self._evaluate_land_use(
                land_use,
                base_suitability,
                terrain,
                env,
                infra,
                risk_result,
                area_km2
            )
            evaluations.append(evaluation)
        
        # Sort by suitability score (descending)
        evaluations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        # Take top N
        top_recommendations = evaluations[:top_n]
        
        # Add ranking
        for i, rec in enumerate(top_recommendations, 1):
            rec['rank'] = i
        
        logger.info(
            f"Top recommendation: {top_recommendations[0]['usage_type']} "
            f"({top_recommendations[0]['suitability_score']:.1f}/10)"
        )
        
        return top_recommendations
    
    def _evaluate_land_use(
        self,
        land_use: str,
        base_suitability: float,
        terrain: Dict,
        env: Dict,
        infra: Dict,
        risk_result,
        area_km2: float
    ) -> Dict:
        """
        Evaluate suitability for specific land use
        
        Args:
            land_use: Land use type
            base_suitability: Base AHP score
            terrain: Terrain features
            env: Environmental features
            infra: Infrastructure features
            risk_result: Risk assessment
            area_km2: Area size
            
        Returns:
            Recommendation dict
        """
        # Start with base suitability
        score = base_suitability
        
        supporting_factors = []
        concerns = []
        
        # Extract key metrics
        slope_avg = terrain.get('slope_avg', 5)
        buildability = terrain.get('buildability_score', 5)
        urbanization = infra.get('urbanization_level', 'suburban')
        road_dist = infra.get('nearest_road_distance', 1000)
        ndvi = env.get('ndvi_avg', 0.5)
        
        # Risk factors
        flood_risk = risk_result.flood.severity if risk_result else 2
        landslide_risk = risk_result.landslide.severity if risk_result else 2
        
        # === RESIDENTIAL USES ===
        if land_use.startswith('residential'):
            # Favor gentle slopes
            if slope_avg < 5:
                score += 1.5
                supporting_factors.append(f"Gentle slope ({slope_avg:.1f}°) ideal for residential")
            elif slope_avg > 15:
                score -= 2.0
                concerns.append(f"Steep slope ({slope_avg:.1f}°) increases construction costs")
            
            # Favor good road access
            if road_dist < 500:
                score += 1.0
                supporting_factors.append(f"Excellent road access ({road_dist:.0f}m)")
            elif road_dist > 2000:
                score -= 1.5
                concerns.append(f"Limited road access ({road_dist/1000:.1f}km)")
            
            # Favor moderate urbanization
            if urbanization in ['suburban', 'urban']:
                score += 1.0
                supporting_factors.append(f"Good location in {urbanization} area")
            elif urbanization == 'remote':
                score -= 1.0
                concerns.append("Remote location may limit demand")
            
            # Risk penalties
            if flood_risk >= 4:
                score -= 1.5
                concerns.append("High flood risk requires mitigation")
            
            if landslide_risk >= 4:
                score -= 1.5
                concerns.append("High landslide risk on steep terrain")
            
            # Type-specific adjustments
            if land_use == 'residential_individual':
                if area_km2 < 0.001:  # < 0.1 hectare
                    concerns.append("Small area may limit development options")
                elif 0.001 <= area_km2 <= 0.01:
                    supporting_factors.append("Ideal size for single-family home")
            
            elif land_use == 'residential_collective':
                if area_km2 < 0.01:
                    score -= 2.0
                    concerns.append("Area too small for collective housing")
                elif area_km2 >= 0.05:
                    score += 1.0
                    supporting_factors.append("Sufficient area for apartment complex")
        
        # === COMMERCIAL USES ===
        elif land_use.startswith('commercial'):
            # Favor urban locations
            if urbanization in ['urban', 'city_center']:
                score += 2.0
                supporting_factors.append("Excellent commercial location")
            elif urbanization == 'suburban':
                score += 0.5
                supporting_factors.append("Good suburban commercial potential")
            else:
                score -= 2.0
                concerns.append("Remote location not suitable for commercial")
            
            # Favor excellent access
            if road_dist < 200:
                score += 1.5
                supporting_factors.append("Prime road frontage")
            elif road_dist > 1000:
                score -= 2.0
                concerns.append("Poor accessibility for commercial")
            
            # Flat terrain preferred
            if slope_avg < 3:
                score += 1.0
                supporting_factors.append("Flat terrain ideal for commercial")
        
        # === INDUSTRIAL USES ===
        elif land_use.startswith('industrial'):
            # Favor larger areas
            if area_km2 < 0.05:
                score -= 2.0
                concerns.append("Area too small for industrial use")
            elif area_km2 >= 0.1:
                score += 1.0
                supporting_factors.append("Adequate space for industrial facility")
            
            # Favor flat terrain
            if slope_avg < 5:
                score += 1.5
                supporting_factors.append("Flat terrain suitable for industrial")
            elif slope_avg > 10:
                score -= 2.0
                concerns.append("Slope too steep for industrial development")
            
            # Prefer away from residential (buffer)
            if urbanization in ['rural', 'remote']:
                score += 0.5
                supporting_factors.append("Sufficient buffer from residential areas")
            
            # Heavy industry needs more space
            if land_use == 'industrial_heavy':
                if area_km2 < 0.2:
                    score -= 2.0
                    concerns.append("Insufficient space for heavy industry")
        
        # === AGRICULTURAL USES ===
        elif land_use.startswith('agricultural'):
            # Favor larger areas
            if area_km2 < 0.1:
                score -= 2.0
                concerns.append("Area too small for viable agriculture")
            elif area_km2 >= 0.5:
                score += 2.0
                supporting_factors.append("Excellent size for agricultural operations")
            
            # Favor moderate slopes (for drainage)
            if 2 <= slope_avg <= 12:
                score += 1.0
                supporting_factors.append("Moderate slope provides good drainage")
            elif slope_avg > 20:
                score -= 2.0
                concerns.append("Too steep for most agricultural uses")
            
            # Vegetation/soil quality
            if ndvi > 0.6:
                score += 2.0
                supporting_factors.append("Excellent vegetation indicates fertile soil")
            elif ndvi < 0.3:
                score -= 1.5
                concerns.append("Poor vegetation suggests soil quality issues")
            
            # Type-specific
            if land_use == 'agricultural_crops':
                if slope_avg > 15:
                    score -= 2.0
                    concerns.append("Too steep for crop farming")
            
            elif land_use == 'agricultural_orchards':
                if 5 <= slope_avg <= 15:
                    score += 1.0
                    supporting_factors.append("Moderate slope ideal for orchards")
        
        # === TOURISM USES ===
        elif land_use.startswith('tourism'):
            # Scenic value (elevation variation)
            elevation_range = terrain.get('elevation_range', 0)
            if elevation_range > 50:
                score += 1.0
                supporting_factors.append("Varied terrain offers scenic views")
            
            # Vegetation/natural beauty
            if ndvi > 0.5:
                score += 1.0
                supporting_factors.append("Green space enhances tourism appeal")
            
            # Access needed
            if road_dist < 1000:
                score += 1.0
                supporting_factors.append("Good accessibility for tourists")
            elif road_dist > 3000:
                score -= 1.5
                concerns.append("Remote location may limit tourist access")
        
        # === MIXED USE ===
        elif land_use == 'mixed_use':
            # Favor urban/suburban
            if urbanization in ['urban', 'suburban']:
                score += 1.5
                supporting_factors.append("Ideal location for mixed-use development")
            
            # Need sufficient area
            if area_km2 < 0.05:
                score -= 1.0
                concerns.append("Limited area for mixed-use")
            elif area_km2 >= 0.1:
                score += 1.0
                supporting_factors.append("Sufficient area for mixed-use complex")
        
        # === SOLAR FARM ===
        elif land_use == 'solar_farm':
            # Need large area
            if area_km2 < 0.1:
                score -= 2.0
                concerns.append("Area too small for solar farm")
            elif area_km2 >= 1.0:
                score += 2.0
                supporting_factors.append("Excellent size for solar installation")
            
            # Flat terrain essential
            if slope_avg < 5:
                score += 2.0
                supporting_factors.append("Flat terrain ideal for solar panels")
            elif slope_avg > 10:
                score -= 2.0
                concerns.append("Slope too steep for solar panels")
        
        # === LOGISTICS/WAREHOUSE ===
        elif land_use == 'logistics_warehouse':
            # Need large flat area
            if area_km2 >= 0.1 and slope_avg < 5:
                score += 2.0
                supporting_factors.append("Perfect for warehouse facility")
            
            # Excellent access required
            motorway_dist = infra.get('motorway_distance', 999999)
            if motorway_dist < 5000:
                score += 1.5
                supporting_factors.append("Excellent highway access")
        
        # Limit score to 0-10
        final_score = max(0, min(10, score))
        
        return {
            'usage_type': self._format_usage_name(land_use),
            'usage_type_code': land_use,
            'suitability_score': round(final_score, 1),
            'supporting_factors': supporting_factors[:5],  # Top 5
            'concerns': concerns[:3],  # Top 3
            'confidence': self._calculate_confidence(supporting_factors, concerns)
        }
    
    def _format_usage_name(self, usage_code: str) -> str:
        """Convert usage code to readable name"""
        name_map = {
            'residential_individual': 'Individual Residential',
            'residential_collective': 'Collective Residential',
            'residential_mixed': 'Mixed Residential',
            'commercial_retail': 'Retail Commercial',
            'commercial_office': 'Office Commercial',
            'industrial_light': 'Light Industrial',
            'industrial_heavy': 'Heavy Industrial',
            'agricultural_crops': 'Agricultural - Crops',
            'agricultural_orchards': 'Agricultural - Orchards',
            'agricultural_livestock': 'Agricultural - Livestock',
            'tourism_hotel': 'Tourism - Hotel',
            'tourism_recreation': 'Tourism - Recreation',
            'mixed_use': 'Mixed-Use Development',
            'solar_farm': 'Solar Energy Farm',
            'logistics_warehouse': 'Logistics & Warehouse'
        }
        return name_map.get(usage_code, usage_code.replace('_', ' ').title())
    
    def _calculate_confidence(
        self,
        supporting_factors: List[str],
        concerns: List[str]
    ) -> float:
        """Calculate confidence in recommendation (0-1)"""
        
        # More supporting factors = higher confidence
        # More concerns = lower confidence
        
        support_score = min(1.0, len(supporting_factors) / 5)
        concern_penalty = min(0.5, len(concerns) / 6)
        
        confidence = 0.5 + support_score * 0.4 - concern_penalty
        
        return round(max(0.3, min(1.0, confidence)), 2)
