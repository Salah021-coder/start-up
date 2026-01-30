# ============================================================================
# FILE: data/feature_extraction/fallback_risk_assessment.py (NEW FILE)
# ============================================================================

from typing import Dict, List
import random

class FallbackRiskAssessment:
    """
    Fallback risk assessment when Earth Engine is not available.
    Provides reasonable estimates based on:
    - Location (Algeria-specific knowledge)
    - Terrain features (if available)
    - General patterns
    """
    
    def __init__(self):
        pass
    
    def assess_all_risks(self, geometry=None, features: Dict = None) -> Dict:
        """
        Generate comprehensive risk assessment without Earth Engine
        Uses location-based estimates and terrain features if available
        """
        
        if not features:
            features = {}
        
        terrain = features.get('terrain', {})
        infra = features.get('infrastructure', {})
        boundary = features.get('boundary', {})
        
        # Get location info
        centroid = boundary.get('centroid', [5.41, 36.19])
        lon, lat = centroid[0], centroid[1]
        
        # Assess all risk types
        risks = {}
        
        risks['flood'] = self._assess_flood_risk(terrain, infra, lat, lon)
        risks['landslide'] = self._assess_landslide_risk(terrain, lat, lon)
        risks['erosion'] = self._assess_erosion_risk(terrain, lat, lon)
        risks['seismic'] = self._assess_seismic_risk(lat, lon)
        risks['drought'] = self._assess_drought_risk(lat, lon)
        risks['wildfire'] = self._assess_wildfire_risk(terrain, lat, lon)
        risks['subsidence'] = self._assess_subsidence_risk(terrain, lat, lon)
        
        # Calculate overall risk
        risks['overall'] = self._calculate_overall_risk(risks)
        
        # Generate summary
        risks['summary'] = self._generate_summary(risks)
        
        # Generate mitigation recommendations
        risks['mitigation'] = self._generate_mitigation(risks)
        
        return risks
    
    def _assess_flood_risk(self, terrain: Dict, infra: Dict, lat: float, lon: float) -> Dict:
        """Assess flood risk based on available data"""
        
        slope = terrain.get('slope_avg', 5.0)
        elevation = terrain.get('elevation_avg', 100.0)
        urban_level = infra.get('urbanization_level', 'suburban')
        
        # Calculate score
        score = 0.0
        
        # Flat areas = higher flood risk
        if slope < 2:
            score += 30.0
        elif slope < 5:
            score += 15.0
        
        # Low elevation
        if elevation < 50:
            score += 25.0
        elif elevation < 100:
            score += 10.0
        
        # Urban areas (potential drainage issues)
        if urban_level == 'urban':
            score += 15.0
        
        # Northern Algeria (more rainfall)
        if lat > 35:
            score += 10.0
        
        # Classify
        if score >= 60:
            level = 'very_high'
            severity = 5
        elif score >= 40:
            level = 'high'
            severity = 4
        elif score >= 20:
            level = 'medium'
            severity = 3
        elif score >= 10:
            level = 'low'
            severity = 2
        else:
            level = 'very_low'
            severity = 1
        
        return {
            'level': level,
            'severity': severity,
            'score': round(score, 1),
            'primary_factors': self._get_flood_factors(slope, elevation, urban_level),
            'description': self._get_flood_description(level),
            'impact': 'May affect construction and require drainage systems' if severity >= 3 else 'Minor impact with standard drainage',
            'affected_area_percent': score * 0.5  # Rough estimate
        }
    
    def _assess_landslide_risk(self, terrain: Dict, lat: float, lon: float) -> Dict:
        """Assess landslide risk"""
        
        slope_avg = terrain.get('slope_avg', 5.0)
        slope_max = terrain.get('slope_max', 10.0)
        elevation_range = terrain.get('elevation_max', 100) - terrain.get('elevation_min', 90)
        
        score = 0.0
        
        # Steep slopes
        if slope_avg > 25:
            score += 40.0
        elif slope_avg > 15:
            score += 25.0
        elif slope_avg > 10:
            score += 10.0
        
        # Maximum slope
        if slope_max > 35:
            score += 25.0
        elif slope_max > 25:
            score += 15.0
        
        # Elevation variation
        if elevation_range > 100:
            score += 20.0
        elif elevation_range > 50:
            score += 10.0
        
        # Northern Algeria (mountainous)
        if lat > 36:
            score += 10.0
        
        # Classify
        if score >= 70:
            level = 'very_high'
            severity = 5
        elif score >= 50:
            level = 'high'
            severity = 4
        elif score >= 30:
            level = 'medium'
            severity = 3
        elif score >= 15:
            level = 'low'
            severity = 2
        else:
            level = 'very_low'
            severity = 1
        
        return {
            'level': level,
            'severity': severity,
            'score': round(score, 1),
            'slope_avg': slope_avg,
            'slope_max': slope_max,
            'elevation_range': elevation_range,
            'primary_factors': [f"Average slope: {slope_avg:.1f}°", f"Max slope: {slope_max:.1f}°"] if slope_avg > 10 else ["Gentle terrain - low risk"],
            'description': 'Steep slopes present - stabilization may be needed' if severity >= 3 else 'Stable terrain',
            'impact': 'Significant slope stabilization required' if severity >= 4 else 'Standard engineering practices sufficient'
        }
    
    def _assess_erosion_risk(self, terrain: Dict, lat: float, lon: float) -> Dict:
        """Assess erosion risk"""
        
        slope = terrain.get('slope_avg', 5.0)
        
        score = 0.0
        
        if slope > 15:
            score += 35.0
        elif slope > 10:
            score += 20.0
        elif slope > 5:
            score += 10.0
        
        # Vegetation estimate (Northern Algeria = better vegetation)
        if lat < 33:  # Southern (Saharan)
            score += 30.0
        elif lat < 35:  # Central
            score += 15.0
        
        # Classify
        if score >= 60:
            level = 'very_high'
            severity = 5
        elif score >= 45:
            level = 'high'
            severity = 4
        elif score >= 25:
            level = 'medium'
            severity = 3
        elif score >= 10:
            level = 'low'
            severity = 2
        else:
            level = 'very_low'
            severity = 1
        
        return {
            'level': level,
            'severity': severity,
            'score': round(score, 1),
            'slope': slope,
            'primary_factors': [f"Slope: {slope:.1f}°", "Vegetation protection estimated"],
            'description': 'Significant erosion risk' if severity >= 3 else 'Low erosion risk',
            'impact': 'Erosion control measures required' if severity >= 3 else 'Standard practices sufficient'
        }
    
    def _assess_seismic_risk(self, lat: float, lon: float) -> Dict:
        """Assess seismic risk (Algeria-specific)"""
        
        # Algeria seismic zones
        if lat > 36:  # Northern coast
            if 2.5 <= lon <= 6.0:  # High activity zone
                score = 75.0
                level = 'very_high'
                severity = 5
                zone = 'IV'
            else:
                score = 60.0
                level = 'high'
                severity = 4
                zone = 'III'
        elif lat > 35:
            score = 50.0
            level = 'high'
            severity = 4
            zone = 'III'
        elif lat > 33:
            score = 35.0
            level = 'medium'
            severity = 3
            zone = 'II'
        else:
            score = 20.0
            level = 'low'
            severity = 2
            zone = 'I'
        
        return {
            'level': level,
            'severity': severity,
            'score': round(score, 1),
            'seismic_zone': zone,
            'latitude': lat,
            'longitude': lon,
            'primary_factors': [f"Seismic Zone {zone}", f"Location: {lat:.2f}°N, {lon:.2f}°E"],
            'description': f'Located in seismic zone {zone}' if severity >= 3 else 'Low seismic activity area',
            'impact': 'Seismic-resistant design required' if severity >= 3 else 'Basic seismic provisions sufficient'
        }
    
    def _assess_drought_risk(self, lat: float, lon: float) -> Dict:
        """Assess drought risk"""
        
        # Based on latitude (climate zones)
        if lat < 32:  # Saharan
            score = 75.0
            level = 'very_high'
            severity = 5
        elif lat < 34:  # Semi-arid
            score = 50.0
            level = 'high'
            severity = 4
        elif lat < 36:  # Moderate
            score = 30.0
            level = 'medium'
            severity = 3
        else:  # Northern (Mediterranean)
            score = 15.0
            level = 'low'
            severity = 2
        
        return {
            'level': level,
            'severity': severity,
            'score': round(score, 1),
            'latitude': lat,
            'primary_factors': [f"Climate zone at {lat:.1f}°N", "Historical rainfall patterns"],
            'description': 'High water scarcity risk' if severity >= 4 else 'Adequate rainfall expected',
            'impact': 'Water storage systems essential' if severity >= 4 else 'Standard water management sufficient'
        }
    
    def _assess_wildfire_risk(self, terrain: Dict, lat: float, lon: float) -> Dict:
        """Assess wildfire risk"""
        
        slope = terrain.get('slope_avg', 5.0)
        
        score = 0.0
        
        # Vegetation (Northern Algeria = more vegetation = higher fire risk)
        if lat > 35:
            score += 30.0
        
        # Slope (fire spreads uphill)
        if slope > 15:
            score += 25.0
        elif slope > 10:
            score += 15.0
        
        # Mediterranean climate = summer fire risk
        if lat > 34:
            score += 15.0
        
        # Classify
        if score >= 60:
            level = 'very_high'
            severity = 5
        elif score >= 45:
            level = 'high'
            severity = 4
        elif score >= 30:
            level = 'medium'
            severity = 3
        elif score >= 15:
            level = 'low'
            severity = 2
        else:
            level = 'very_low'
            severity = 1
        
        return {
            'level': level,
            'severity': severity,
            'score': round(score, 1),
            'slope': slope,
            'primary_factors': [f"Mediterranean climate zone", f"Slope: {slope:.1f}°"] if severity >= 3 else ["Low fire risk conditions"],
            'description': 'Elevated wildfire risk' if severity >= 3 else 'Low wildfire risk',
            'impact': 'Fire breaks and defensible space recommended' if severity >= 3 else 'Basic fire safety sufficient'
        }
    
    def _assess_subsidence_risk(self, terrain: Dict, lat: float, lon: float) -> Dict:
        """Assess subsidence risk"""
        
        elevation = terrain.get('elevation_avg', 100.0)
        slope = terrain.get('slope_avg', 5.0)
        
        score = 0.0
        
        # Low, flat areas
        if elevation < 50 and slope < 2:
            score = 40.0
            level = 'high'
            severity = 4
        elif elevation < 100 and slope < 3:
            score = 25.0
            level = 'medium'
            severity = 3
        else:
            score = 15.0
            level = 'low'
            severity = 2
        
        return {
            'level': level,
            'severity': severity,
            'score': round(score, 1),
            'elevation': elevation,
            'slope': slope,
            'primary_factors': [f"Elevation: {elevation:.0f}m", f"Slope: {slope:.1f}°"],
            'description': 'Possible soft soils' if severity >= 3 else 'Stable ground conditions',
            'impact': 'Soil investigation recommended' if severity >= 3 else 'Standard foundations sufficient'
        }
    
    def _calculate_overall_risk(self, risks: Dict) -> Dict:
        """Calculate overall risk profile"""
        
        risk_types = ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']
        
        severities = [risks[rt]['severity'] for rt in risk_types if rt in risks]
        avg_severity = sum(severities) / len(severities) if severities else 2.0
        
        high_count = sum(1 for rt in risk_types if risks.get(rt, {}).get('severity', 0) >= 4)
        medium_count = sum(1 for rt in risk_types if risks.get(rt, {}).get('severity', 0) == 3)
        
        # Determine overall level
        if high_count >= 3:
            overall_level = 'very_high'
        elif high_count >= 2:
            overall_level = 'high'
        elif high_count >= 1 or medium_count >= 3:
            overall_level = 'medium'
        elif medium_count >= 1:
            overall_level = 'low'
        else:
            overall_level = 'very_low'
        
        return {
            'level': overall_level,
            'average_severity': round(avg_severity, 2),
            'high_risk_count': high_count,
            'medium_risk_count': medium_count,
            'total_risks_assessed': len(severities)
        }
    
    def _generate_summary(self, risks: Dict) -> List[str]:
        """Generate risk summary"""
        
        overall = risks.get('overall', {})
        summary = []
        
        # Major risks
        major_risks = []
        for risk_type in ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']:
            if risk_type in risks:
                if risks[risk_type]['severity'] >= 4:
                    major_risks.append(f"{risk_type.title()}: {risks[risk_type]['level'].replace('_', ' ').title()}")
        
        if major_risks:
            summary.append(f"⚠️ **Major Risks:** {', '.join(major_risks)}")
        else:
            summary.append("✅ **No major risks identified**")
        
        summary.append(f"📊 **Overall Risk Level:** {overall.get('level', 'medium').replace('_', ' ').title()}")
        summary.append(f"📈 **Average Severity:** {overall.get('average_severity', 2.5):.1f}/5")
        summary.append(f"ℹ️ **Note:** Assessment based on location and terrain analysis (Earth Engine not available)")
        
        return summary
    
    def _generate_mitigation(self, risks: Dict) -> List[str]:
        """Generate mitigation recommendations"""
        
        recommendations = []
        
        for risk_type in ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']:
            if risk_type in risks and risks[risk_type]['severity'] >= 3:
                if risk_type == 'flood':
                    recommendations.append("🌊 **Flood:** Install drainage systems, consider elevation, obtain flood insurance")
                elif risk_type == 'landslide':
                    recommendations.append("⛰️ **Landslide:** Implement slope stabilization, use retaining walls")
                elif risk_type == 'erosion':
                    recommendations.append("🌾 **Erosion:** Plant vegetation, install erosion control measures")
                elif risk_type == 'seismic':
                    recommendations.append("🏗️ **Seismic:** Follow seismic building codes, use flexible foundations")
                elif risk_type == 'drought':
                    recommendations.append("💧 **Drought:** Install water storage, implement conservation measures")
                elif risk_type == 'wildfire':
                    recommendations.append("🔥 **Wildfire:** Create defensible space, use fire-resistant materials")
                elif risk_type == 'subsidence':
                    recommendations.append("🏚️ **Subsidence:** Conduct soil investigation, consider deep foundations")
        
        if not recommendations:
            recommendations.append("✅ **No major mitigation required** - standard practices sufficient")
        
        return recommendations
    
    def _get_flood_factors(self, slope: float, elevation: float, urban: str) -> List[str]:
        """Get flood risk factors"""
        factors = []
        
        if slope < 3:
            factors.append(f"Very flat terrain: {slope:.1f}°")
        if elevation < 100:
            factors.append(f"Low elevation: {elevation:.0f}m")
        if urban == 'urban':
            factors.append("Urban area - potential drainage issues")
        
        if not factors:
            factors.append("No significant flood indicators")
        
        return factors
    
    def _get_flood_description(self, level: str) -> str:
        """Get flood description"""
        descriptions = {
            'very_high': 'Severe flood risk - frequent flooding expected',
            'high': 'Significant flood risk - flooding likely during heavy rain',
            'medium': 'Moderate flood risk - occasional flooding possible',
            'low': 'Low flood risk - flooding unlikely',
            'very_low': 'Minimal flood risk - well-drained area'
        }
        return descriptions.get(level, 'Risk level uncertain')
