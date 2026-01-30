# ============================================================================
# FILE: core/risk/rules.py
# Rule-based risk assessment thresholds and scoring
# ============================================================================

from typing import Tuple
from core.risk.risk_engine import RiskLevel


class RiskRules:
    """
    All rule-based risk scoring logic
    
    PHILOSOPHY:
    - Thresholds based on engineering standards
    - Conservative (favor safety)
    - Documented sources where possible
    """
    
    # ========== FLOOD RISK ==========
    
    def calculate_flood_score(
        self,
        slope_avg: float,
        elevation: float,
        water_occurrence: float = 0
    ) -> float:
        """
        Calculate flood risk score (0-100)
        
        Args:
            slope_avg: Average slope in degrees
            elevation: Elevation in meters
            water_occurrence: Water occurrence percentage (0-100)
            
        Returns:
            Flood risk score (0-100)
        """
        score = 0.0
        
        # Slope contribution (40%)
        if slope_avg < 2:
            score += 40.0  # Very flat - poor drainage
        elif slope_avg < 5:
            score += 25.0  # Flat - moderate drainage
        elif slope_avg < 10:
            score += 10.0  # Gentle - good drainage
        else:
            score += 0.0   # Steep - excellent drainage
        
        # Elevation contribution (35%)
        if elevation < 50:
            score += 35.0
        elif elevation < 100:
            score += 20.0
        elif elevation < 200:
            score += 10.0
        else:
            score += 0.0
        
        # Water occurrence contribution (25%)
        score += (water_occurrence / 100) * 25.0
        
        return min(100.0, score)
    
    def get_flood_description(self, level: RiskLevel) -> str:
        """Get flood risk description"""
        descriptions = {
            RiskLevel.VERY_HIGH: 'Severe flood risk - frequent flooding expected',
            RiskLevel.HIGH: 'Significant flood risk - flooding likely during heavy rain',
            RiskLevel.MEDIUM: 'Moderate flood risk - occasional flooding possible',
            RiskLevel.LOW: 'Low flood risk - flooding unlikely under normal conditions',
            RiskLevel.VERY_LOW: 'Minimal flood risk - well-drained area'
        }
        return descriptions.get(level, 'Unknown flood risk')
    
    def get_flood_impact(self, severity: int) -> str:
        """Get flood impact description"""
        if severity >= 4:
            return 'Comprehensive drainage systems and elevation required'
        elif severity >= 3:
            return 'Drainage infrastructure recommended'
        else:
            return 'Standard drainage practices sufficient'
    
    # ========== LANDSLIDE RISK ==========
    
    def calculate_landslide_score(
        self,
        slope_avg: float,
        slope_max: float,
        elevation_range: float = 0
    ) -> float:
        """Calculate landslide risk score (0-100)"""
        score = 0.0
        
        # Average slope (40%)
        if slope_avg > 25:
            score += 40.0
        elif slope_avg > 15:
            score += 30.0
        elif slope_avg > 10:
            score += 15.0
        elif slope_avg > 5:
            score += 5.0
        
        # Maximum slope (40%)
        if slope_max > 35:
            score += 40.0
        elif slope_max > 25:
            score += 30.0
        elif slope_max > 15:
            score += 15.0
        elif slope_max > 10:
            score += 5.0
        
        # Elevation variation (20%)
        if elevation_range > 100:
            score += 20.0
        elif elevation_range > 50:
            score += 10.0
        
        return min(100.0, score)
    
    def get_landslide_description(self, level: RiskLevel) -> str:
        """Get landslide risk description"""
        descriptions = {
            RiskLevel.VERY_HIGH: 'Critical landslide risk - unstable slopes',
            RiskLevel.HIGH: 'High landslide risk - slope stabilization essential',
            RiskLevel.MEDIUM: 'Moderate landslide risk - engineering assessment needed',
            RiskLevel.LOW: 'Low landslide risk - standard precautions sufficient',
            RiskLevel.VERY_LOW: 'Minimal landslide risk - stable terrain'
        }
        return descriptions.get(level, 'Unknown landslide risk')
    
    def get_landslide_impact(self, severity: int) -> str:
        """Get landslide impact description"""
        if severity >= 4:
            return 'Extensive slope stabilization and retaining walls essential'
        elif severity >= 3:
            return 'Slope stabilization measures recommended'
        else:
            return 'Standard engineering practices sufficient'
    
    # ========== EROSION RISK ==========
    
    def calculate_erosion_score(
        self,
        slope: float,
        vegetation_cover: float  # NDVI value
    ) -> float:
        """Calculate erosion risk score (0-100)"""
        score = 0.0
        
        # Slope contribution (60%)
        if slope > 15:
            score += 40.0
        elif slope > 10:
            score += 25.0
        elif slope > 5:
            score += 10.0
        
        # Vegetation protection (40%)
        # Lower NDVI = less protection = higher score
        vegetation_protection = max(0, 1 - vegetation_cover)
        score += vegetation_protection * 40.0
        
        return min(100.0, score)
    
    def get_erosion_description(self, level: RiskLevel) -> str:
        """Get erosion risk description"""
        descriptions = {
            RiskLevel.VERY_HIGH: 'Severe erosion risk - rapid soil loss expected',
            RiskLevel.HIGH: 'High erosion risk - protective measures essential',
            RiskLevel.MEDIUM: 'Moderate erosion risk - erosion control recommended',
            RiskLevel.LOW: 'Low erosion risk - minor measures sufficient',
            RiskLevel.VERY_LOW: 'Minimal erosion risk - stable soil'
        }
        return descriptions.get(level, 'Unknown erosion risk')
    
    def get_erosion_impact(self, severity: int) -> str:
        """Get erosion impact description"""
        if severity >= 4:
            return 'Comprehensive erosion control structures required'
        elif severity >= 3:
            return 'Erosion control measures recommended'
        else:
            return 'Basic erosion prevention sufficient'
    
    # ========== SEISMIC RISK ==========
    
    def calculate_seismic_score(
        self,
        latitude: float,
        longitude: float
    ) -> Tuple[float, str]:
        """
        Calculate seismic risk score based on Algeria seismic zones
        
        Returns:
            (score, zone)
        """
        # Algeria seismic zonation (simplified)
        # Based on RPA 99 Version 2003 (Algerian seismic code)
        
        if latitude > 36:  # Northern coast
            if 2.5 <= longitude <= 6.0:  # High activity zone
                return 85.0, 'IV'
            else:
                return 65.0, 'III'
        elif latitude > 35:  # Tell Atlas
            return 60.0, 'III'
        elif latitude > 33:  # High plateaus
            return 40.0, 'II'
        else:  # Sahara
            return 20.0, 'I'
    
    def get_seismic_description(self, level: RiskLevel, zone: str) -> str:
        """Get seismic risk description"""
        return f'Seismic Zone {zone} - {level.name.replace("_", " ").lower()} seismic activity'
    
    def get_seismic_impact(self, severity: int) -> str:
        """Get seismic impact description"""
        if severity >= 4:
            return 'Strict seismic-resistant design required per RPA 99/2003'
        elif severity >= 3:
            return 'Seismic building codes apply - flexible foundations required'
        else:
            return 'Basic seismic provisions sufficient'
    
    # ========== DROUGHT RISK ==========
    
    def calculate_drought_score(
        self,
        latitude: float,
        vegetation_health: float  # NDVI
    ) -> float:
        """Calculate drought risk score based on climate zone"""
        score = 0.0
        
        # Climate zone contribution (70%)
        if latitude < 32:  # Saharan
            score += 70.0
        elif latitude < 34:  # Semi-arid
            score += 45.0
        elif latitude < 36:  # Sub-humid
            score += 25.0
        else:  # Mediterranean
            score += 10.0
        
        # Vegetation health indicator (30%)
        # Lower NDVI suggests drought stress
        if vegetation_health < 0.3:
            score += 30.0
        elif vegetation_health < 0.5:
            score += 15.0
        
        return min(100.0, score)
    
    def get_drought_description(self, level: RiskLevel) -> str:
        """Get drought risk description"""
        descriptions = {
            RiskLevel.VERY_HIGH: 'Severe water scarcity risk',
            RiskLevel.HIGH: 'High drought risk - water resources limited',
            RiskLevel.MEDIUM: 'Moderate drought risk - irrigation may be needed',
            RiskLevel.LOW: 'Low drought risk - adequate water availability',
            RiskLevel.VERY_LOW: 'Minimal drought risk - good water resources'
        }
        return descriptions.get(level, 'Unknown drought risk')
    
    def get_drought_impact(self, severity: int) -> str:
        """Get drought impact description"""
        if severity >= 4:
            return 'Water storage systems and conservation essential'
        elif severity >= 3:
            return 'Water conservation systems recommended'
        else:
            return 'Standard water management sufficient'
    
    # ========== WILDFIRE RISK ==========
    
    def calculate_wildfire_score(
        self,
        slope: float,
        vegetation_density: float  # NDVI
    ) -> float:
        """Calculate wildfire risk score"""
        score = 0.0
        
        # Vegetation (fuel) contribution (60%)
        # Higher NDVI = more vegetation = more fuel
        if vegetation_density > 0.6:
            score += 35.0
        elif vegetation_density > 0.4:
            score += 20.0
        
        # Slope contribution (fire spreads uphill) (40%)
        if slope > 15:
            score += 25.0
        elif slope > 10:
            score += 15.0
        elif slope > 5:
            score += 8.0
        
        return min(100.0, score)
    
    def get_wildfire_description(self, level: RiskLevel) -> str:
        """Get wildfire risk description"""
        descriptions = {
            RiskLevel.VERY_HIGH: 'Critical wildfire risk',
            RiskLevel.HIGH: 'High wildfire risk - fire prevention essential',
            RiskLevel.MEDIUM: 'Moderate wildfire risk - fire breaks recommended',
            RiskLevel.LOW: 'Low wildfire risk - basic safety sufficient',
            RiskLevel.VERY_LOW: 'Minimal wildfire risk'
        }
        return descriptions.get(level, 'Unknown wildfire risk')
    
    def get_wildfire_impact(self, severity: int) -> str:
        """Get wildfire impact description"""
        if severity >= 4:
            return 'Fire breaks and defensible space essential'
        elif severity >= 3:
            return 'Fire safety measures recommended'
        else:
            return 'Basic fire safety sufficient'
    
    # ========== SUBSIDENCE RISK ==========
    
    def calculate_subsidence_score(
        self,
        elevation: float,
        slope: float
    ) -> float:
        """Calculate subsidence risk score"""
        score = 0.0
        
        # Low, flat areas at higher risk
        if elevation < 50 and slope < 2:
            score = 50.0
        elif elevation < 100 and slope < 3:
            score = 30.0
        else:
            score = 15.0
        
        return score
    
    def get_subsidence_description(self, level: RiskLevel) -> str:
        """Get subsidence risk description"""
        descriptions = {
            RiskLevel.VERY_HIGH: 'High subsidence risk - detailed investigation required',
            RiskLevel.HIGH: 'Elevated subsidence risk - soil investigation recommended',
            RiskLevel.MEDIUM: 'Moderate subsidence risk - foundation assessment advised',
            RiskLevel.LOW: 'Low subsidence risk - standard practices sufficient',
            RiskLevel.VERY_LOW: 'Minimal subsidence risk'
        }
        return descriptions.get(level, 'Unknown subsidence risk')
    
    def get_subsidence_impact(self, severity: int) -> str:
        """Get subsidence impact description"""
        if severity >= 4:
            return 'Detailed soil investigation and deep foundations required'
        elif severity >= 3:
            return 'Soil investigation and foundation assessment recommended'
        else:
            return 'Standard foundation practices sufficient'
    
    # ========== UNIVERSAL METHODS ==========
    
    def score_to_level_severity(self, score: float) -> Tuple[RiskLevel, int]:
        """
        Convert score to risk level and severity
        
        Args:
            score: Risk score (0-100)
            
        Returns:
            (RiskLevel, severity_1_to_5)
        """
        if score >= 70:
            return RiskLevel.VERY_HIGH, 5
        elif score >= 50:
            return RiskLevel.HIGH, 4
        elif score >= 30:
            return RiskLevel.MEDIUM, 3
        elif score >= 15:
            return RiskLevel.LOW, 2
        else:
            return RiskLevel.VERY_LOW, 1
    
    def get_mitigation_recommendation(
        self,
        risk_type: str,
        severity: int
    ) -> str:
        """Get mitigation recommendation for a specific risk"""
        
        if severity < 3:
            return None  # No special mitigation needed
        
        recommendations = {
            'flood': '🌊 **Flood:** Install comprehensive drainage systems, consider elevation',
            'landslide': '⛰️ **Landslide:** Slope stabilization and retaining walls required',
            'erosion': '🌾 **Erosion:** Install erosion control structures and vegetation cover',
            'seismic': '🏗️ **Seismic:** Follow seismic building codes, use flexible foundations',
            'drought': '💧 **Drought:** Install water storage and conservation systems',
            'wildfire': '🔥 **Wildfire:** Create defensible space and fire breaks',
            'subsidence': '🏚️ **Subsidence:** Conduct soil investigation and consider deep foundations'
        }
        
        return recommendations.get(risk_type)
