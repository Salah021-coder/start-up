# ============================================================================
# FILE: data/feature_extraction/risk_assessment.py (NEW FILE)
# ============================================================================

import ee
from typing import Dict, List
from data.earth_engine.gee_client import GEEClient
import numpy as np

class ComprehensiveRiskAssessment:
    """
    Comprehensive risk assessment for land evaluation
    Evaluates multiple risk types:
    - Flood risk
    - Landslide risk
    - Erosion risk
    - Seismic risk
    - Drought risk
    - Wildfire risk
    - Subsidence risk
    """
    
    def __init__(self):
        self.gee_client = GEEClient()
    
    def assess_all_risks(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Perform comprehensive risk assessment
        
        Args:
            geometry: Earth Engine geometry
            features: Extracted features (terrain, environmental, etc.)
        
        Returns:
            Dict containing all risk assessments
        """
        
        risks = {}
        
        # 1. Flood Risk
        risks['flood'] = self._assess_flood_risk(geometry, features)
        
        # 2. Landslide Risk
        risks['landslide'] = self._assess_landslide_risk(geometry, features)
        
        # 3. Erosion Risk
        risks['erosion'] = self._assess_erosion_risk(geometry, features)
        
        # 4. Seismic Risk
        risks['seismic'] = self._assess_seismic_risk(geometry, features)
        
        # 5. Drought Risk
        risks['drought'] = self._assess_drought_risk(geometry, features)
        
        # 6. Wildfire Risk
        risks['wildfire'] = self._assess_wildfire_risk(geometry, features)
        
        # 7. Subsidence Risk
        risks['subsidence'] = self._assess_subsidence_risk(geometry, features)
        
        # Calculate overall risk profile
        risks['overall'] = self._calculate_overall_risk(risks)
        
        # Generate risk summary
        risks['summary'] = self._generate_risk_summary(risks)
        
        # Risk mitigation recommendations
        risks['mitigation'] = self._generate_mitigation_recommendations(risks)
        
        return risks
    
    # ========================================================================
    # FLOOD RISK ASSESSMENT
    # ========================================================================
    
    def _assess_flood_risk(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Assess flood risk using multiple indicators:
        - Water occurrence data
        - Elevation relative to water bodies
        - Slope (drainage)
        - Precipitation patterns
        """
        
        try:
            # Get water occurrence from JRC dataset
            water_data = self.gee_client.get_water_occurrence(geometry)
            water_occurrence = water_data.get('water_occurrence_avg', 0) or 0
            
            # Get terrain data
            terrain = features.get('terrain', {})
            slope = terrain.get('slope_avg', 5) or 5
            elevation = terrain.get('elevation_avg', 100) or 100
            
            # Calculate flood risk score (0-100)
            flood_score = 0
            
            # Water occurrence is primary indicator
            flood_score += water_occurrence * 0.6
            
            # Low slope increases flood risk
            if slope < 2:
                flood_score += 20
            elif slope < 5:
                flood_score += 10
            
            # Low elevation near water increases risk
            if elevation < 50 and water_occurrence > 10:
                flood_score += 20
            
            # Classify risk level
            if flood_score >= 60:
                level = 'very_high'
                severity = 5
            elif flood_score >= 40:
                level = 'high'
                severity = 4
            elif flood_score >= 20:
                level = 'medium'
                severity = 3
            elif flood_score >= 10:
                level = 'low'
                severity = 2
            else:
                level = 'very_low'
                severity = 1
            
            return {
                'level': level,
                'severity': severity,
                'score': round(flood_score, 1),
                'water_occurrence': water_occurrence,
                'affected_area_percent': water_occurrence,
                'primary_factors': self._get_flood_factors(slope, elevation, water_occurrence),
                'description': self._get_flood_description(level),
                'impact': self._get_flood_impact(level)
            }
            
        except Exception as e:
            print(f"Error assessing flood risk: {e}")
            return self._default_risk_assessment('flood')
    
    def _get_flood_factors(self, slope: float, elevation: float, water_occ: float) -> List[str]:
        """Identify primary flood risk factors"""
        factors = []
        
        if water_occ > 30:
            factors.append(f"High water occurrence: {water_occ:.0f}%")
        if slope < 2:
            factors.append(f"Very flat terrain: {slope:.1f}° (poor drainage)")
        if elevation < 50:
            factors.append(f"Low elevation: {elevation:.0f}m (flood-prone)")
        
        if not factors:
            factors.append("No significant flood indicators detected")
        
        return factors
    
    def _get_flood_description(self, level: str) -> str:
        """Get flood risk description"""
        descriptions = {
            'very_high': 'Severe flood risk - area experiences frequent flooding',
            'high': 'Significant flood risk - flooding likely during heavy rainfall',
            'medium': 'Moderate flood risk - occasional flooding possible',
            'low': 'Low flood risk - flooding unlikely under normal conditions',
            'very_low': 'Minimal flood risk - well-drained area'
        }
        return descriptions.get(level, 'Unknown risk level')
    
    def _get_flood_impact(self, level: str) -> str:
        """Get flood impact description"""
        impacts = {
            'very_high': 'May render land undevelopable; requires major flood protection infrastructure',
            'high': 'Significant impact on construction and insurance costs; flood mitigation required',
            'medium': 'Moderate impact; proper drainage systems recommended',
            'low': 'Minor impact; standard drainage sufficient',
            'very_low': 'Negligible impact on development'
        }
        return impacts.get(level, 'Unknown impact')
    
    # ========================================================================
    # LANDSLIDE RISK ASSESSMENT
    # ========================================================================
    
    def _assess_landslide_risk(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Assess landslide risk based on:
        - Slope steepness
        - Elevation variation
        - Soil type/vegetation cover
        - Precipitation
        """
        
        try:
            terrain = features.get('terrain', {})
            env = features.get('environmental', {})
            
            slope_avg = terrain.get('slope_avg', 0) or 0
            slope_max = terrain.get('slope_max', 0) or 0
            elevation_max = terrain.get('elevation_max', 0) or 0
            elevation_min = terrain.get('elevation_min', 0) or 0
            elevation_range = elevation_max - elevation_min
            ndvi = env.get('ndvi_avg', 0.5) or 0.5
            
            # Calculate landslide risk score
            landslide_score = 0
            
            # Steep slopes are primary factor
            if slope_avg > 30:
                landslide_score += 40
            elif slope_avg > 20:
                landslide_score += 30
            elif slope_avg > 15:
                landslide_score += 20
            elif slope_avg > 10:
                landslide_score += 10
            
            # Maximum slope
            if slope_max > 40:
                landslide_score += 30
            elif slope_max > 30:
                landslide_score += 20
            
            # Elevation variation
            if elevation_range > 100:
                landslide_score += 20
            elif elevation_range > 50:
                landslide_score += 10
            
            # Poor vegetation (less soil stability)
            if ndvi < 0.3:
                landslide_score += 10
            
            # Classify risk
            if landslide_score >= 70:
                level = 'very_high'
                severity = 5
            elif landslide_score >= 50:
                level = 'high'
                severity = 4
            elif landslide_score >= 30:
                level = 'medium'
                severity = 3
            elif landslide_score >= 15:
                level = 'low'
                severity = 2
            else:
                level = 'very_low'
                severity = 1
            
            return {
                'level': level,
                'severity': severity,
                'score': round(landslide_score, 1),
                'slope_avg': slope_avg,
                'slope_max': slope_max,
                'elevation_range': elevation_range,
                'primary_factors': self._get_landslide_factors(slope_avg, slope_max, elevation_range),
                'description': self._get_landslide_description(level),
                'impact': self._get_landslide_impact(level)
            }
            
        except Exception as e:
            print(f"Error assessing landslide risk: {e}")
            return self._default_risk_assessment('landslide')
    
    def _get_landslide_factors(self, slope_avg: float, slope_max: float, elev_range: float) -> List[str]:
        """Identify landslide risk factors"""
        factors = []
        
        if slope_avg > 25:
            factors.append(f"Very steep average slope: {slope_avg:.1f}°")
        elif slope_avg > 15:
            factors.append(f"Steep slopes: {slope_avg:.1f}°")
        
        if slope_max > 35:
            factors.append(f"Extremely steep areas: {slope_max:.1f}° maximum")
        
        if elev_range > 100:
            factors.append(f"High elevation variation: {elev_range:.0f}m")
        
        if not factors:
            factors.append("Gentle terrain - landslide risk minimal")
        
        return factors
    
    def _get_landslide_description(self, level: str) -> str:
        """Get landslide risk description"""
        descriptions = {
            'very_high': 'Critical landslide risk - unstable slopes present',
            'high': 'Significant landslide risk - slope stabilization essential',
            'medium': 'Moderate landslide risk - engineering assessment recommended',
            'low': 'Low landslide risk - standard precautions sufficient',
            'very_low': 'Minimal landslide risk - stable terrain'
        }
        return descriptions.get(level, 'Unknown risk level')
    
    def _get_landslide_impact(self, level: str) -> str:
        """Get landslide impact description"""
        impacts = {
            'very_high': 'Development extremely hazardous; may require relocation or extensive engineering',
            'high': 'Major constraints on development; expensive slope stabilization needed',
            'medium': 'Moderate impact; proper grading and retaining walls required',
            'low': 'Minor impact; standard engineering practices sufficient',
            'very_low': 'Negligible impact on development'
        }
        return impacts.get(level, 'Unknown impact')
    
    # ========================================================================
    # EROSION RISK ASSESSMENT
    # ========================================================================
    
    def _assess_erosion_risk(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Assess soil erosion risk based on:
        - Slope
        - Vegetation cover
        - Soil type
        - Precipitation
        """
        
        try:
            terrain = features.get('terrain', {})
            env = features.get('environmental', {})
            
            slope = terrain.get('slope_avg', 0) or 0
            ndvi = env.get('ndvi_avg', 0.5) or 0.5
            
            # Calculate erosion risk score
            erosion_score = 0
            
            # Slope factor
            if slope > 15:
                erosion_score += 30
            elif slope > 10:
                erosion_score += 20
            elif slope > 5:
                erosion_score += 10
            
            # Vegetation cover (protects against erosion)
            if ndvi < 0.2:
                erosion_score += 40  # Bare soil
            elif ndvi < 0.4:
                erosion_score += 25  # Sparse vegetation
            elif ndvi < 0.6:
                erosion_score += 10  # Moderate vegetation
            # Good vegetation (ndvi > 0.6) reduces risk
            
            # Classify risk
            if erosion_score >= 60:
                level = 'very_high'
                severity = 5
            elif erosion_score >= 45:
                level = 'high'
                severity = 4
            elif erosion_score >= 25:
                level = 'medium'
                severity = 3
            elif erosion_score >= 10:
                level = 'low'
                severity = 2
            else:
                level = 'very_low'
                severity = 1
            
            return {
                'level': level,
                'severity': severity,
                'score': round(erosion_score, 1),
                'slope': slope,
                'vegetation_cover': ndvi,
                'primary_factors': self._get_erosion_factors(slope, ndvi),
                'description': self._get_erosion_description(level),
                'impact': self._get_erosion_impact(level)
            }
            
        except Exception as e:
            print(f"Error assessing erosion risk: {e}")
            return self._default_risk_assessment('erosion')
    
    def _get_erosion_factors(self, slope: float, ndvi: float) -> List[str]:
        """Identify erosion risk factors"""
        factors = []
        
        if slope > 15:
            factors.append(f"Steep slopes: {slope:.1f}° (high runoff)")
        
        if ndvi < 0.3:
            factors.append(f"Poor vegetation cover: NDVI {ndvi:.2f}")
        elif ndvi > 0.6:
            factors.append(f"Good vegetation cover: NDVI {ndvi:.2f} (protective)")
        
        if not factors:
            factors.append("Moderate conditions - standard erosion control needed")
        
        return factors
    
    def _get_erosion_description(self, level: str) -> str:
        """Get erosion risk description"""
        descriptions = {
            'very_high': 'Severe erosion risk - rapid soil loss expected',
            'high': 'Significant erosion risk - protective measures essential',
            'medium': 'Moderate erosion risk - erosion control recommended',
            'low': 'Low erosion risk - basic measures sufficient',
            'very_low': 'Minimal erosion risk - stable soil'
        }
        return descriptions.get(level, 'Unknown risk level')
    
    def _get_erosion_impact(self, level: str) -> str:
        """Get erosion impact description"""
        impacts = {
            'very_high': 'Severe soil degradation; expensive erosion control required',
            'high': 'Significant soil loss; terracing and vegetation establishment needed',
            'medium': 'Moderate soil loss; erosion control measures recommended',
            'low': 'Minor soil loss; basic erosion control sufficient',
            'very_low': 'Negligible soil loss'
        }
        return impacts.get(level, 'Unknown impact')
    
    # ========================================================================
    # SEISMIC RISK ASSESSMENT
    # ========================================================================
    
    def _assess_seismic_risk(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Assess earthquake/seismic risk
        Note: For Algeria, using known seismic zones
        """
        
        try:
            # Get centroid coordinates
            coords = geometry.centroid().coordinates().getInfo()
            lon, lat = coords[0], coords[1]
            
            # Algeria seismic zones (simplified)
            # Northern Algeria (Tell Atlas) is more seismically active
            seismic_score = self._calculate_algeria_seismic_risk(lat, lon)
            
            # Classify risk
            if seismic_score >= 70:
                level = 'very_high'
                severity = 5
                zone = 'IV'
            elif seismic_score >= 50:
                level = 'high'
                severity = 4
                zone = 'III'
            elif seismic_score >= 30:
                level = 'medium'
                severity = 3
                zone = 'II'
            else:
                level = 'low'
                severity = 2
                zone = 'I'
            
            return {
                'level': level,
                'severity': severity,
                'score': round(seismic_score, 1),
                'seismic_zone': zone,
                'latitude': lat,
                'primary_factors': self._get_seismic_factors(zone, lat),
                'description': self._get_seismic_description(level),
                'impact': self._get_seismic_impact(level)
            }
            
        except Exception as e:
            print(f"Error assessing seismic risk: {e}")
            return self._default_risk_assessment('seismic')
    
    def _calculate_algeria_seismic_risk(self, lat: float, lon: float) -> float:
        """
        Calculate seismic risk for Algeria based on known seismic zones
        Northern coastal areas are high risk (Tell Atlas, active faults)
        """
        
        # High risk zone: Northern Algeria (coastal areas, Tell Atlas)
        if lat > 36.0:  # Northern coastal region
            if 2.5 <= lon <= 6.0:  # Algiers-Oran region (very active)
                return 75
            else:
                return 60
        
        # Medium-high risk: North-central
        elif lat > 35.0:
            return 50
        
        # Medium risk: Central plateau
        elif lat > 33.0:
            return 35
        
        # Lower risk: Saharan region
        else:
            return 20
    
    def _get_seismic_factors(self, zone: str, lat: float) -> List[str]:
        """Identify seismic risk factors"""
        factors = []
        
        if lat > 36.0:
            factors.append("Located in Northern Algeria (Tell Atlas region - active seismic zone)")
        
        factors.append(f"Seismic Zone {zone} - building codes apply")
        
        return factors
    
    def _get_seismic_description(self, level: str) -> str:
        """Get seismic risk description"""
        descriptions = {
            'very_high': 'Very high seismic activity - major earthquakes possible',
            'high': 'Significant seismic activity - moderate to strong earthquakes likely',
            'medium': 'Moderate seismic activity - seismic design required',
            'low': 'Low seismic activity - basic seismic precautions sufficient'
        }
        return descriptions.get(level, 'Unknown risk level')
    
    def _get_seismic_impact(self, level: str) -> str:
        """Get seismic impact description"""
        impacts = {
            'very_high': 'Strict seismic design required; significantly higher construction costs',
            'high': 'Seismic-resistant design essential; increased construction costs',
            'medium': 'Seismic design standards must be followed',
            'low': 'Basic seismic provisions sufficient'
        }
        return impacts.get(level, 'Unknown impact')
    
    # ========================================================================
    # DROUGHT RISK ASSESSMENT
    # ========================================================================
    
    def _assess_drought_risk(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Assess drought risk based on:
        - Historical precipitation
        - Water availability
        - Vegetation stress indicators
        """
        
        try:
            coords = geometry.centroid().coordinates().getInfo()
            lat = coords[1]
            
            env = features.get('environmental', {})
            ndvi = env.get('ndvi_avg', 0.5)
            
            # Calculate drought risk (higher score = higher risk)
            drought_score = 0
            
            # Latitude-based (Algeria): Southern = more arid
            if lat < 32:  # Saharan region
                drought_score += 60
            elif lat < 34:  # Saharan Atlas
                drought_score += 40
            elif lat < 36:  # High Plateaus
                drought_score += 25
            else:  # Tell/Coastal
                drought_score += 10
            
            # Vegetation health indicator
            if ndvi < 0.2:  # Very sparse vegetation
                drought_score += 20
            elif ndvi < 0.4:  # Sparse vegetation
                drought_score += 10
            
            # Classify risk
            if drought_score >= 70:
                level = 'very_high'
                severity = 5
            elif drought_score >= 50:
                level = 'high'
                severity = 4
            elif drought_score >= 30:
                level = 'medium'
                severity = 3
            elif drought_score >= 15:
                level = 'low'
                severity = 2
            else:
                level = 'very_low'
                severity = 1
            
            return {
                'level': level,
                'severity': severity,
                'score': round(drought_score, 1),
                'latitude': lat,
                'vegetation_health': ndvi,
                'primary_factors': self._get_drought_factors(lat, ndvi),
                'description': self._get_drought_description(level),
                'impact': self._get_drought_impact(level)
            }
            
        except Exception as e:
            print(f"Error assessing drought risk: {e}")
            return self._default_risk_assessment('drought')
    
    def _get_drought_factors(self, lat: float, ndvi: float) -> List[str]:
        """Identify drought risk factors"""
        factors = []
        
        if lat < 32:
            factors.append("Saharan region - extremely arid climate")
        elif lat < 34:
            factors.append("Semi-arid region - limited rainfall")
        elif lat < 36:
            factors.append("Moderate rainfall zone")
        else:
            factors.append("Coastal/northern region - adequate rainfall")
        
        if ndvi < 0.3:
            factors.append(f"Low vegetation: NDVI {ndvi:.2f} (water stress indicator)")
        
        return factors
    
    def _get_drought_description(self, level: str) -> str:
        """Get drought risk description"""
        descriptions = {
            'very_high': 'Extreme drought risk - water scarcity severe',
            'high': 'High drought risk - water resources limited',
            'medium': 'Moderate drought risk - irrigation may be needed',
            'low': 'Low drought risk - adequate water availability',
            'very_low': 'Minimal drought risk - good water resources'
        }
        return descriptions.get(level, 'Unknown risk level')
    
    def _get_drought_impact(self, level: str) -> str:
        """Get drought impact description"""
        impacts = {
            'very_high': 'Severe water scarcity; expensive water infrastructure required',
            'high': 'Significant water challenges; irrigation systems essential',
            'medium': 'Moderate water concerns; water conservation recommended',
            'low': 'Minor water concerns; standard water management sufficient',
            'very_low': 'Adequate water resources available'
        }
        return impacts.get(level, 'Unknown impact')
    
    # ========================================================================
    # WILDFIRE RISK ASSESSMENT
    # ========================================================================
    
    def _assess_wildfire_risk(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Assess wildfire risk based on:
        - Vegetation type and density
        - Climate (dry conditions)
        - Topography
        """
        
        try:
            terrain = features.get('terrain', {})
            env = features.get('environmental', {})
            coords = geometry.centroid().coordinates().getInfo()
            lat = coords[1] if coords else 36.0
            
            slope = terrain.get('slope_avg', 0) or 0
            ndvi = env.get('ndvi_avg', 0.5) or 0.5
            
            # Calculate wildfire risk
            wildfire_score = 0
            
            # Vegetation density (fuel load)
            if 0.4 < ndvi < 0.7:  # Moderate vegetation = higher fire risk
                wildfire_score += 30
            elif ndvi > 0.7:  # Dense vegetation
                wildfire_score += 20
            elif ndvi < 0.2:  # Bare ground - low fuel
                wildfire_score += 5
            
            # Slope (fire spreads faster uphill)
            if slope > 20:
                wildfire_score += 25
            elif slope > 10:
                wildfire_score += 15
            
            # Climate zone (Northern Algeria more vegetated, higher risk)
            if lat > 35:
                wildfire_score += 20
            
            # Classify risk
            if wildfire_score >= 60:
                level = 'very_high'
                severity = 5
            elif wildfire_score >= 45:
                level = 'high'
                severity = 4
            elif wildfire_score >= 30:
                level = 'medium'
                severity = 3
            elif wildfire_score >= 15:
                level = 'low'
                severity = 2
            else:
                level = 'very_low'
                severity = 1
            
            return {
                'level': level,
                'severity': severity,
                'score': round(wildfire_score, 1),
                'vegetation_density': ndvi,
                'slope': slope,
                'primary_factors': self._get_wildfire_factors(ndvi, slope),
                'description': self._get_wildfire_description(level),
                'impact': self._get_wildfire_impact(level)
            }
            
        except Exception as e:
            print(f"Error assessing wildfire risk: {e}")
            return self._default_risk_assessment('wildfire')
    
    def _get_wildfire_factors(self, ndvi: float, slope: float) -> List[str]:
        """Identify wildfire risk factors"""
        factors = []
        
        if 0.4 < ndvi < 0.7:
            factors.append(f"Moderate vegetation density: NDVI {ndvi:.2f} (fuel present)")
        elif ndvi > 0.7:
            factors.append(f"Dense vegetation: NDVI {ndvi:.2f} (high fuel load)")
        
        if slope > 15:
            factors.append(f"Steep slopes: {slope:.1f}° (fire spreads rapidly uphill)")
        
        if not factors:
            factors.append("Low wildfire risk conditions")
        
        return factors
    
    def _get_wildfire_description(self, level: str) -> str:
        """Get wildfire risk description"""
        descriptions = {
            'very_high': 'Critical wildfire risk - high fuel loads and favorable conditions',
            'high': 'Significant wildfire risk - fire prevention essential',
            'medium': 'Moderate wildfire risk - fire breaks recommended',
            'low': 'Low wildfire risk - basic fire safety sufficient',
            'very_low': 'Minimal wildfire risk'
        }
        return descriptions.get(level, 'Unknown risk level')
    
    def _get_wildfire_impact(self, level: str) -> str:
        """Get wildfire impact description"""
        impacts = {
            'very_high': 'Severe threat to structures; expensive fire protection required',
            'high': 'Significant threat; fire breaks and defensible space essential',
            'medium': 'Moderate threat; fire-resistant landscaping recommended',
            'low': 'Minor threat; basic fire safety measures sufficient',
            'very_low': 'Negligible fire threat'
        }
        return impacts.get(level, 'Unknown impact')
    
    # ========================================================================
    # SUBSIDENCE RISK ASSESSMENT
    # ========================================================================
    
    def _assess_subsidence_risk(self, geometry: ee.Geometry, features: Dict) -> Dict:
        """
        Assess land subsidence risk based on:
        - Soil type
        - Water extraction
        - Terrain characteristics
        """
        
        try:
            terrain = features.get('terrain', {})
            
            # Simplified subsidence risk for Algeria
            # Higher risk in areas with:
            # - Soft soils
            # - Low elevation
            # - Flat terrain (possible soft sediments)
            
            elevation = terrain.get('elevation_avg', 100) or 100
            slope = terrain.get('slope_avg', 5) or 5
            
            subsidence_score = 0
            
            # Very flat, low-lying areas
            if elevation < 50 and slope < 2:
                subsidence_score += 40
            elif elevation < 100 and slope < 3:
                subsidence_score += 20
            
            # Add generic risk (would need soil data for better assessment)
            subsidence_score += 10
            
            # Classify risk
            if subsidence_score >= 50:
                level = 'high'
                severity = 4
            elif subsidence_score >= 30:
                level = 'medium'
                severity = 3
            elif subsidence_score >= 15:
                level = 'low'
                severity = 2
            else:
                level = 'very_low'
                severity = 1
            
            return {
                'level': level,
                'severity': severity,
                'score': round(subsidence_score, 1),
                'elevation': elevation,
                'slope': slope,
                'primary_factors': self._get_subsidence_factors(elevation, slope),
                'description': self._get_subsidence_description(level),
                'impact': self._get_subsidence_impact(level)
            }
            
        except Exception as e:
            print(f"Error assessing subsidence risk: {e}")
            return self._default_risk_assessment('subsidence')
    
    def _get_subsidence_factors(self, elevation: float, slope: float) -> List[str]:
        """Identify subsidence risk factors"""
        factors = []
        
        if elevation < 50 and slope < 2:
            factors.append(f"Low, flat area: {elevation:.0f}m elevation, {slope:.1f}° slope")
            factors.append("Possible soft sediments or high water table")
        else:
            factors.append("Terrain characteristics suggest low subsidence risk")
        
        return factors
    
    def _get_subsidence_description(self, level: str) -> str:
        """Get subsidence risk description"""
        descriptions = {
            'high': 'Elevated subsidence risk - soil investigation required',
            'medium': 'Moderate subsidence risk - foundation assessment recommended',
            'low': 'Low subsidence risk - standard foundation practices',
            'very_low': 'Minimal subsidence risk'
        }
        return descriptions.get(level, 'Unknown risk level')
    
    def _get_subsidence_impact(self, level: str) -> str:
        """Get subsidence impact description"""
        impacts = {
            'high': 'Potential structural damage; deep foundations may be required',
            'medium': 'Possible settling; foundation monitoring recommended',
            'low': 'Minor settling possible; standard foundations sufficient',
            'very_low': 'Negligible subsidence expected'
        }
        return impacts.get(level, 'Unknown impact')
    
    # ========================================================================
    # OVERALL RISK AGGREGATION
    # ========================================================================
    
    def _calculate_overall_risk(self, risks: Dict) -> Dict:
        """Calculate overall risk profile"""
        
        # Get all individual risks
        risk_types = ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']
        
        # Calculate average severity
        severities = [risks[rt]['severity'] for rt in risk_types if rt in risks]
        avg_severity = np.mean(severities) if severities else 2
        
        # Count high and very high risks
        high_risks = sum(1 for rt in risk_types if rt in risks and risks[rt]['severity'] >= 4)
        medium_risks = sum(1 for rt in risk_types if rt in risks and risks[rt]['severity'] == 3)
        
        # Determine overall level
        if high_risks >= 3 or avg_severity >= 4:
            overall_level = 'very_high'
        elif high_risks >= 2 or avg_severity >= 3.5:
            overall_level = 'high'
        elif high_risks >= 1 or medium_risks >= 3:
            overall_level = 'medium'
        elif medium_risks >= 1:
            overall_level = 'low'
        else:
            overall_level = 'very_low'
        
        return {
            'level': overall_level,
            'average_severity': round(avg_severity, 2),
            'high_risk_count': high_risks,
            'medium_risk_count': medium_risks,
            'total_risks_assessed': len(severities)
        }
    
    def _generate_risk_summary(self, risks: Dict) -> List[str]:
        """Generate human-readable risk summary"""
        summary = []
        
        # Identify major risks
        major_risks = []
        for risk_type in ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']:
            if risk_type in risks and risks[risk_type]['severity'] >= 4:
                major_risks.append(f"{risk_type.title()}: {risks[risk_type]['level'].replace('_', ' ').title()}")
        
        if major_risks:
            summary.append(f"⚠️ **Major Risks Identified:** {', '.join(major_risks)}")
        else:
            summary.append("✅ **No major risks identified**")
        
        # Add overall assessment
        overall = risks['overall']
        summary.append(f"📊 **Overall Risk Level:** {overall['level'].replace('_', ' ').title()}")
        summary.append(f"📈 **Average Risk Severity:** {overall['average_severity']:.1f}/5")
        
        return summary
    
    def _generate_mitigation_recommendations(self, risks: Dict) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # Flood mitigation
        if risks.get('flood', {}).get('severity', 0) >= 3:
            recommendations.append("🌊 **Flood:** Install comprehensive drainage systems, consider flood insurance, elevate structures")
        
        # Landslide mitigation
        if risks.get('landslide', {}).get('severity', 0) >= 3:
            recommendations.append("⛰️ **Landslide:** Implement slope stabilization, retaining walls, avoid construction on steep areas")
        
        # Erosion mitigation
        if risks.get('erosion', {}).get('severity', 0) >= 3:
            recommendations.append("🌾 **Erosion:** Plant vegetation, install erosion control structures, terracing on slopes")
        
        # Seismic mitigation
        if risks.get('seismic', {}).get('severity', 0) >= 3:
            recommendations.append("🏗️ **Seismic:** Follow seismic building codes, use flexible foundations, conduct soil analysis")
        
        # Drought mitigation
        if risks.get('drought', {}).get('severity', 0) >= 3:
            recommendations.append("💧 **Drought:** Install water storage systems, implement water conservation, consider drought-resistant landscaping")
        
        # Wildfire mitigation
        if risks.get('wildfire', {}).get('severity', 0) >= 3:
            recommendations.append("🔥 **Wildfire:** Create defensible space, use fire-resistant materials, maintain fire breaks")
        
        # Subsidence mitigation
        if risks.get('subsidence', {}).get('severity', 0) >= 3:
            recommendations.append("🏚️ **Subsidence:** Conduct soil investigation, use deep foundations, monitor for settling")
        
        if not recommendations:
            recommendations.append("✅ **No major mitigation required** - standard construction practices sufficient")
        
        return recommendations
    
    def _default_risk_assessment(self, risk_type: str) -> Dict:
        """Return default risk assessment when data unavailable"""
        return {
            'level': 'unknown',
            'severity': 0,
            'score': 0,
            'primary_factors': ['Data unavailable'],
            'description': 'Risk assessment unavailable - data not accessible',
            'impact': 'Unknown - professional assessment recommended'
        }
