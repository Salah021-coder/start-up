# ============================================================================
# FILE: core/analysis_processor.py (ENHANCED VERSION WITH COMPREHENSIVE RISKS)
# ============================================================================

from typing import Dict
from utils.ee_manager import EarthEngineManager
from utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisProcessor:
    """Coordinate the overall analysis workflow with enhanced criteria and comprehensive risk assessment"""
    
    def __init__(self, use_real_osm: bool = True):
        self.ee_available = EarthEngineManager.is_available()
        self.use_real_osm = use_real_osm
        
        # Initialize EE-dependent modules if available
        if self.ee_available:
            try:
                from data.earth_engine.gee_client import GEEClient
                from data.feature_extraction.terrain_features import TerrainFeatureExtractor
                from data.feature_extraction.environmental_features import EnvironmentalFeatureExtractor
                
                self.gee_client = GEEClient()
                self.terrain_extractor = TerrainFeatureExtractor()
                self.env_extractor = EnvironmentalFeatureExtractor()
            except Exception as e:
                print(f"Warning: Could not initialize EE extractors: {e}")
                self.ee_available = False
        
        # Initialize other modules
        from data.feature_extraction.infrastructure_features import InfrastructureFeatureExtractor
        from intelligence.ahp.ahp_solver import AHPSolver
        from intelligence.ml.models.suitability_predictor import SuitabilityPredictor
        from intelligence.recommendation.score_aggregator import ScoreAggregator
        
        self.infra_extractor = InfrastructureFeatureExtractor(use_real_osm=use_real_osm)
        self.ahp_solver = AHPSolver()
        self.ml_predictor = SuitabilityPredictor()
        self.score_aggregator = ScoreAggregator()
    
    def run_analysis(
        self,
        boundary_data: Dict,
        criteria: Dict,
        progress_callback=None
    ) -> Dict:
        """Run complete enhanced land evaluation analysis"""
        
        try:
            logger.info("Starting enhanced land evaluation analysis with comprehensive risk assessment")
            
            # Step 1: Extract features
            if progress_callback:
                progress_callback("Extracting features (this may take 30-60 seconds)...", 10)
            
            features = self._extract_all_features(boundary_data)
            
            if progress_callback:
                progress_callback("Features extracted successfully", 35)
            
            # Step 2: Auto-select and adjust criteria based on features
            if progress_callback:
                progress_callback("Auto-selecting optimal criteria...", 40)
            
            from core.criteria_engine import CriteriaEngine
            criteria_engine = CriteriaEngine()
            
            # Get infrastructure features for criteria selection
            infra_features = features.get('infrastructure', {})
            adjusted_criteria = criteria_engine.auto_select_criteria(
                boundary_data,
                infra_features
            )
            
            # Step 3: Run AHP analysis with enhanced criteria
            if progress_callback:
                progress_callback("Running enhanced AHP multi-criteria analysis...", 55)
            
            ahp_results = self.ahp_solver.solve(features, adjusted_criteria['criteria'])
            
            # Step 4: Run ML predictions
            if progress_callback:
                progress_callback("Running ML suitability predictions...", 75)
            
            ml_results = self.ml_predictor.predict(features)
            
            # Step 5: Aggregate scores
            if progress_callback:
                progress_callback("Aggregating results and generating recommendations...", 90)
            
            final_scores = self.score_aggregator.aggregate(
                ahp_results,
                ml_results,
                features
            )
            
            # Step 6: Compile results with enhanced insights
            results = self._compile_results(
                boundary_data,
                features,
                adjusted_criteria,
                ahp_results,
                ml_results,
                final_scores
            )
            
            if progress_callback:
                progress_callback("Analysis complete!", 100)
            
            logger.info("Enhanced analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _extract_all_features(self, boundary_data: Dict) -> Dict:
        """Extract all features including enhanced infrastructure data and comprehensive risks"""
        
        ee_geometry = boundary_data.get('ee_geometry')
        shapely_geometry = boundary_data.get('geometry')
        centroid = boundary_data.get('centroid')
        
        features = {}
        
        print("\n=== Feature Extraction Started ===")
        
        # Extract terrain features (requires EE)
        print("1/3: Extracting terrain features...")
        if self.ee_available and ee_geometry:
            try:
                features['terrain'] = self.terrain_extractor.extract(ee_geometry)
                print("✓ Terrain features extracted")
            except Exception as e:
                print(f"⚠ Terrain extraction failed: {e}")
                features['terrain'] = self._get_default_terrain()
        else:
            features['terrain'] = self._get_default_terrain()
            print("ℹ Using default terrain features (EE not available)")
        
        # Extract environmental features (requires EE) - NOW WITH COMPREHENSIVE RISK ASSESSMENT
        print("2/3: Extracting environmental features and comprehensive risk assessment...")
        if self.ee_available and ee_geometry:
            try:
                # Pass terrain features to environmental extractor for better risk assessment
                features['environmental'] = self.env_extractor.extract(
                    ee_geometry,
                    terrain_features=features['terrain']  # Pass terrain for risk calculation
                )
                print("✓ Environmental features extracted")
                
                # Display risk summary if available
                comprehensive_risks = features['environmental'].get('comprehensive_risks', {})
                if comprehensive_risks:
                    print("\n  === Risk Assessment Summary ===")
                    overall = comprehensive_risks.get('overall', {})
                    print(f"  Overall Risk Level: {overall.get('level', 'unknown').replace('_', ' ').title()}")
                    print(f"  High Risks: {overall.get('high_risk_count', 0)}, Medium Risks: {overall.get('medium_risk_count', 0)}")
                    
                    # Show critical risks
                    for risk_type in ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']:
                        risk_data = comprehensive_risks.get(risk_type, {})
                        if risk_data.get('severity', 0) >= 4:  # High or Very High
                            print(f"  ⚠️ {risk_type.title()}: {risk_data.get('level', 'unknown').replace('_', ' ').title()}")
                    print("  ================================\n")
                    
            except Exception as e:
                print(f"⚠ Environmental extraction failed: {e}")
                features['environmental'] = self._get_default_environmental()
        else:
            features['environmental'] = self._get_default_environmental()
            print("ℹ Using default environmental features (EE not available)")
        
        # Extract enhanced infrastructure features
        print("3/3: Extracting enhanced infrastructure features...")
        if self.use_real_osm:
            print("   → Fetching real data from OpenStreetMap (may take 30-60s)...")
        
        try:
            features['infrastructure'] = self.infra_extractor.extract(
                ee_geometry=ee_geometry,
                centroid=centroid,
                geometry=shapely_geometry
            )
            print(f"✓ Infrastructure features extracted (quality: {features['infrastructure'].get('data_quality')})")
        except Exception as e:
            print(f"⚠ Infrastructure extraction failed: {e}")
            features['infrastructure'] = self._get_default_infrastructure()
        
        features['boundary'] = boundary_data
        
        print("=== Feature Extraction Complete ===\n")
        
        return features
    
    def _compile_results(
        self,
        boundary_data: Dict,
        features: Dict,
        criteria: Dict,
        ahp_results: Dict,
        ml_results: Dict,
        final_scores: Dict
    ) -> Dict:
        """Compile all results with enhanced insights"""
        
        # Generate enhanced insights (now includes comprehensive risks)
        enhanced_insights = self._generate_enhanced_insights(features, final_scores)
        
        return {
            'analysis_id': self._generate_analysis_id(),
            'timestamp': self._get_timestamp(),
            'boundary': boundary_data,
            'features': features,
            'criteria': criteria,
            'ahp_results': ahp_results,
            'ml_results': ml_results,
            'final_scores': final_scores,
            'overall_score': final_scores['overall_score'],
            'confidence_level': final_scores['confidence'],
            'recommendations': final_scores['recommendations'],
            'risk_assessment': final_scores['risk_assessment'],
            'key_insights': enhanced_insights,
            'data_sources': self._get_data_sources(features)
        }
    
    def _generate_enhanced_insights(self, features: Dict, scores: Dict) -> Dict:
        """Generate comprehensive insights from all features including comprehensive risks"""
        insights = {
            'strengths': [],
            'concerns': [],
            'opportunities': [],
            'location_summary': '',
            'accessibility_summary': '',
            'development_potential': ''
        }
        
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        # Get comprehensive risks
        comprehensive_risks = env.get('comprehensive_risks', {})
        
        # === STRENGTHS ===
        
        # Terrain strengths
        if terrain.get('slope_avg', 999) < 5:
            insights['strengths'].append(
                f"Excellent terrain: Gentle slope ({terrain.get('slope_avg', 0):.1f}°) ideal for all types of construction"
            )
        
        # Infrastructure strengths
        road_dist = infra.get('nearest_road_distance', 999999)
        if road_dist < 500:
            road_type = infra.get('road_type', 'road')
            insights['strengths'].append(
                f"Superior accessibility: {road_type.title()} road only {road_dist:.0f}m away"
            )
        
        # Urban proximity
        urban_dist = infra.get('nearest_city_distance', 999999)
        city_name = infra.get('city_name', 'city')
        if urban_dist < 10000:
            insights['strengths'].append(
                f"Prime location: Only {urban_dist/1000:.1f}km from {city_name}"
            )
        
        # Amenities
        total_amenities = infra.get('total_amenities', 0)
        if total_amenities > 30:
            insights['strengths'].append(
                f"Rich amenities: {total_amenities} services within 3km radius"
            )
        
        # Public transport
        transport_score = infra.get('public_transport_score', 0)
        if transport_score > 7:
            insights['strengths'].append(
                f"Excellent public transport: Score {transport_score:.1f}/10"
            )
        
        # Utilities
        utilities_count = sum([
            infra.get('electricity_grid', False),
            infra.get('water_network', False),
            infra.get('sewage_system', False),
            infra.get('internet_fiber', False)
        ])
        if utilities_count >= 3:
            insights['strengths'].append(
                f"Complete infrastructure: {utilities_count}/4 major utilities available"
            )
        
        # Low risk strengths
        if comprehensive_risks:
            low_risk_count = 0
            for risk_type in ['flood', 'landslide', 'erosion', 'wildfire']:
                risk_data = comprehensive_risks.get(risk_type, {})
                if risk_data.get('severity', 5) <= 2:  # Low or very low
                    low_risk_count += 1
            
            if low_risk_count >= 3:
                insights['strengths'].append(
                    f"Low environmental risks: Minimal {', '.join([r for r in ['flood', 'landslide', 'erosion', 'wildfire'] if comprehensive_risks.get(r, {}).get('severity', 5) <= 2])} risk"
                )
        
        # === CONCERNS (Now includes comprehensive risks) ===
        
        # Terrain concerns
        if terrain.get('slope_avg', 0) > 15:
            insights['concerns'].append(
                f"Steep terrain: {terrain.get('slope_avg', 0):.1f}° slope may increase construction costs by 20-40%"
            )
        
        # COMPREHENSIVE RISK CONCERNS
        if comprehensive_risks:
            # Flood risk
            flood = comprehensive_risks.get('flood', {})
            if flood.get('severity', 0) >= 4:
                insights['concerns'].append(
                    f"🌊 HIGH FLOOD RISK: {flood.get('description', 'Significant flooding expected')} - {flood.get('impact', '')}"
                )
            elif flood.get('severity', 0) >= 3:
                insights['concerns'].append(
                    f"🌊 Moderate flood risk: {flood.get('affected_area_percent', 0):.0f}% of area - drainage infrastructure recommended"
                )
            
            # Landslide risk
            landslide = comprehensive_risks.get('landslide', {})
            if landslide.get('severity', 0) >= 4:
                insights['concerns'].append(
                    f"⛰️ HIGH LANDSLIDE RISK: {landslide.get('description', 'Unstable slopes')} - Slope stabilization essential"
                )
            elif landslide.get('severity', 0) >= 3:
                insights['concerns'].append(
                    f"⛰️ Moderate landslide risk: Slopes up to {landslide.get('slope_max', 0):.1f}° - engineering assessment needed"
                )
            
            # Erosion risk
            erosion = comprehensive_risks.get('erosion', {})
            if erosion.get('severity', 0) >= 4:
                insights['concerns'].append(
                    f"🌾 HIGH EROSION RISK: {erosion.get('description', 'Rapid soil loss expected')} - Erosion control essential"
                )
            
            # Seismic risk
            seismic = comprehensive_risks.get('seismic', {})
            if seismic.get('severity', 0) >= 4:
                insights['concerns'].append(
                    f"🏗️ HIGH SEISMIC RISK: Zone {seismic.get('seismic_zone', 'Unknown')} - Strict seismic building codes required"
                )
            elif seismic.get('severity', 0) >= 3:
                insights['concerns'].append(
                    f"🏗️ Moderate seismic risk: {seismic.get('description', 'Seismic design required')}"
                )
            
            # Drought risk
            drought = comprehensive_risks.get('drought', {})
            if drought.get('severity', 0) >= 4:
                insights['concerns'].append(
                    f"💧 HIGH DROUGHT RISK: {drought.get('description', 'Water scarcity severe')} - Water storage systems essential"
                )
            
            # Wildfire risk
            wildfire = comprehensive_risks.get('wildfire', {})
            if wildfire.get('severity', 0) >= 4:
                insights['concerns'].append(
                    f"🔥 HIGH WILDFIRE RISK: {wildfire.get('description', 'Critical fire risk')} - Fire prevention essential"
                )
            
            # Subsidence risk
            subsidence = comprehensive_risks.get('subsidence', {})
            if subsidence.get('severity', 0) >= 3:
                insights['concerns'].append(
                    f"🏚️ Subsidence risk: {subsidence.get('description', 'Soil investigation needed')}"
                )
        
        # Legacy flood risk (for backward compatibility)
        else:
            flood_risk = env.get('flood_risk_percent', 0)
            if flood_risk > 30:
                insights['concerns'].append(
                    f"Significant flood risk: {flood_risk:.0f}% of area affected - consider drainage infrastructure"
                )
            elif flood_risk > 10:
                insights['concerns'].append(
                    f"Moderate flood risk: {flood_risk:.0f}% of area - mitigation recommended"
                )
        
        # Accessibility concerns
        if road_dist > 2000:
            insights['concerns'].append(
                f"Limited road access: Nearest road {road_dist/1000:.1f}km away - consider access road development"
            )
        
        # Isolation concerns
        if total_amenities < 10:
            insights['concerns'].append(
                f"Limited services: Only {total_amenities} amenities nearby - residents will need to travel for services"
            )
        
        # Urban distance
        if urban_dist > 30000:
            insights['concerns'].append(
                f"Remote location: {urban_dist/1000:.0f}km from nearest city - limited market access"
            )
        
        # === OPPORTUNITIES ===
        
        # Development pressure
        dev_pressure = infra.get('development_pressure', 'low')
        if dev_pressure == 'high':
            insights['opportunities'].append(
                "High development pressure: Area experiencing rapid growth - strong appreciation potential"
            )
        elif dev_pressure == 'medium':
            insights['opportunities'].append(
                "Growing area: Moderate development activity - good timing for investment"
            )
        
        # Growth zone
        if infra.get('growth_zone', False):
            insights['opportunities'].append(
                "Designated growth zone: Government planning may bring infrastructure improvements"
            )
        
        # Top recommendation opportunity
        top_rec = scores.get('recommendations', [{}])[0] if scores.get('recommendations') else {}
        if top_rec.get('suitability_score', 0) > 8:
            insights['opportunities'].append(
                f"Exceptional suitability: {top_rec.get('usage_type', 'development').title()} development has {top_rec.get('suitability_score', 0):.1f}/10 score"
            )
        
        # Market opportunities
        urbanization = infra.get('urbanization_level', 'rural')
        if urbanization == 'suburban':
            insights['opportunities'].append(
                "Suburban location: Ideal for residential development serving urban workers"
            )
        
        # === SUMMARIES ===
        
        # Location summary
        insights['location_summary'] = f"{city_name}, {urbanization} area with {dev_pressure} development pressure"
        
        # Accessibility summary
        access_score = infra.get('accessibility_score', 5)
        if access_score > 7:
            access_level = "Excellent"
        elif access_score > 5:
            access_level = "Good"
        else:
            access_level = "Limited"
        
        insights['accessibility_summary'] = f"{access_level} accessibility (Score: {access_score:.1f}/10) - {road_dist:.0f}m to nearest road"
        
        # Development potential (now factors in comprehensive risks)
        overall_score = scores.get('overall_score', 5)
        
        # Adjust for high risks
        if comprehensive_risks:
            overall_risk = comprehensive_risks.get('overall', {})
            high_risk_count = overall_risk.get('high_risk_count', 0)
            
            if high_risk_count >= 3:
                potential = "Limited development potential - multiple high-risk factors require extensive mitigation"
            elif high_risk_count >= 2:
                potential = "Moderate development potential - significant risk mitigation required"
            elif overall_score > 8:
                potential = "Exceptional development potential with manageable risk factors"
            elif overall_score > 6:
                potential = "Strong development potential with standard risk mitigation"
            elif overall_score > 4:
                potential = "Moderate development potential - careful planning and risk assessment required"
            else:
                potential = "Limited development potential - significant constraints present"
        else:
            # Fallback without comprehensive risks
            if overall_score > 8:
                potential = "Exceptional development potential with minimal constraints"
            elif overall_score > 6:
                potential = "Strong development potential with manageable challenges"
            elif overall_score > 4:
                potential = "Moderate development potential - careful planning required"
            else:
                potential = "Limited development potential - significant constraints present"
        
        insights['development_potential'] = potential
        
        return insights
    
    def _get_data_sources(self, features: Dict) -> Dict:
        """Document data sources used in analysis"""
        sources = {
            'terrain': 'Default values' if not self.ee_available else 'Google Earth Engine (SRTM)',
            'environmental': 'Default values' if not self.ee_available else 'Google Earth Engine (Sentinel-2, ESA WorldCover)',
            'infrastructure': features.get('infrastructure', {}).get('data_quality', 'unknown'),
            'risk_assessment': 'Comprehensive (7 risk types)' if features.get('environmental', {}).get('comprehensive_risks') else 'Basic (flood only)'
        }
        
        return sources
    
    # Keep existing helper methods...
    def _get_default_terrain(self) -> Dict:
        return {
            'slope_avg': 5.0,
            'slope_min': 0.0,
            'slope_max': 15.0,
            'elevation_avg': 100.0,
            'elevation_min': 90.0,
            'elevation_max': 110.0,
            'elevation_std': 5.0,
            'aspect_degrees': 180.0,
            'aspect_direction': 'S',
            'terrain_classification': 'gentle',
            'buildability_score': 7.0,
            'data_quality': 'default'
        }
    
    def _get_default_environmental(self) -> Dict:
        return {
            'ndvi_avg': 0.5,
            'ndvi_min': 0.2,
            'ndvi_max': 0.8,
            'land_cover_distribution': {},
            'dominant_cover': 'grassland',
            'water_occurrence_avg': 5.0,
            'water_occurrence_max': 10.0,
            'flood_risk_level': 'low',
            'flood_risk_percent': 5.0,
            'air_quality_estimate': 'good',
            'environmental_score': 7.0,
            'data_quality': 'default'
        }
    
    def _get_default_infrastructure(self) -> Dict:
        return {
            'nearest_road_distance': 1000.0,
            'road_type': 'secondary',
            'motorway_distance': 15000.0,
            'primary_road_distance': 3000.0,
            'secondary_road_distance': 1000.0,
            'road_density': 2.0,
            'city_name': 'Unknown',
            'nearest_city_distance': 15000.0,
            'urbanization_level': 'suburban',
            'population_density': 500,
            'development_pressure': 'medium',
            'growth_zone': False,
            'bus_stop_distance': 1000.0,
            'train_station_distance': 20000.0,
            'public_transport_score': 5.0,
            'schools_count_3km': 2,
            'hospitals_count_5km': 1,
            'total_amenities': 15,
            'electricity_grid': True,
            'water_network': True,
            'sewage_system': True,
            'gas_network': False,
            'internet_fiber': True,
            'accessibility_score': 6.0,
            'infrastructure_score': 6.0,
            'urban_development_score': 5.0,
            'data_quality': 'default'
        }
    
    def _generate_analysis_id(self) -> str:
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"LAND_{timestamp}_{unique_id}"
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
