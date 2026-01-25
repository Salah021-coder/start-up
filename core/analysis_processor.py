# ============================================================================
# FILE: core/analysis_processor.py (COMPLETE WITH ERROR HANDLING)
# ============================================================================

from typing import Dict
from utils.ee_manager import EarthEngineManager
from utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisProcessor:
    """Coordinate the overall analysis workflow"""
    
    def __init__(self):
        self.ee_available = EarthEngineManager.is_available()
        
        # Only import EE-dependent modules if available
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
        
        # These don't require EE
        from data.feature_extraction.infrastructure_features import InfrastructureFeatureExtractor
        from intelligence.ahp.ahp_solver import AHPSolver
        from intelligence.ml.models.suitability_predictor import SuitabilityPredictor
        from intelligence.recommendation.score_aggregator import ScoreAggregator
        
        self.infra_extractor = InfrastructureFeatureExtractor()
        self.ahp_solver = AHPSolver()
        self.ml_predictor = SuitabilityPredictor()
        self.score_aggregator = ScoreAggregator()
    
    def run_analysis(
        self,
        boundary_data: Dict,
        criteria: Dict,
        progress_callback=None
    ) -> Dict:
        """Run complete land evaluation analysis"""
        
        try:
            logger.info("Starting land evaluation analysis")
            
            # Step 1: Extract features
            if progress_callback:
                progress_callback("Extracting features from multiple sources...", 20)
            
            features = self._extract_all_features(boundary_data)
            
            if progress_callback:
                progress_callback("Features extracted successfully", 40)
            
            # Step 2: Run AHP analysis
            if progress_callback:
                progress_callback("Running AHP multi-criteria analysis...", 60)
            
            ahp_results = self.ahp_solver.solve(features, criteria)
            
            # Step 3: Run ML predictions
            if progress_callback:
                progress_callback("Running ML suitability predictions...", 80)
            
            ml_results = self.ml_predictor.predict(features)
            
            # Step 4: Aggregate scores
            if progress_callback:
                progress_callback("Aggregating results...", 90)
            
            final_scores = self.score_aggregator.aggregate(
                ahp_results,
                ml_results,
                features
            )
            
            # Step 5: Compile results
            results = self._compile_results(
                boundary_data,
                features,
                criteria,
                ahp_results,
                ml_results,
                final_scores
            )
            
            if progress_callback:
                progress_callback("Analysis complete!", 100)
            
            logger.info("Analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _extract_all_features(self, boundary_data: Dict) -> Dict:
        """Extract features from all data sources"""
        
        ee_geometry = boundary_data.get('ee_geometry')
        shapely_geometry = boundary_data.get('geometry')
        centroid = boundary_data.get('centroid')
        
        features = {}
        
        # Extract terrain features (requires EE)
        if self.ee_available and ee_geometry:
            try:
                features['terrain'] = self.terrain_extractor.extract(ee_geometry)
            except Exception as e:
                print(f"Warning: Terrain extraction failed: {e}")
                features['terrain'] = self._get_default_terrain()
        else:
            features['terrain'] = self._get_default_terrain()
        
        # Extract environmental features (requires EE)
        if self.ee_available and ee_geometry:
            try:
                features['environmental'] = self.env_extractor.extract(ee_geometry)
            except Exception as e:
                print(f"Warning: Environmental extraction failed: {e}")
                features['environmental'] = self._get_default_environmental()
        else:
            features['environmental'] = self._get_default_environmental()
        
        # Extract infrastructure features (doesn't require EE)
        try:
            features['infrastructure'] = self.infra_extractor.extract(
                ee_geometry=ee_geometry,
                centroid=centroid,
                geometry=shapely_geometry
            )
        except Exception as e:
            print(f"Warning: Infrastructure extraction failed: {e}")
            features['infrastructure'] = self._get_default_infrastructure()
        
        features['boundary'] = boundary_data
        
        return features
    
    def _get_default_terrain(self) -> Dict:
        """Default terrain features"""
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
        """Default environmental features"""
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
        """Default infrastructure features"""
        return {
            'nearest_road_distance': 1000.0,
            'road_type': 'secondary',
            'utilities_available': {
                'water': True,
                'electricity': True,
                'gas': False,
                'sewage': True,
                'internet': True
            },
            'nearby_amenities': {
                'schools': 1,
                'hospitals': 1,
                'shopping': 2,
                'restaurants': 3,
                'parks': 1
            },
            'accessibility_score': 6.0,
            'infrastructure_score': 6.0,
            'data_quality': 'default'
        }
    
    def _compile_results(
        self,
        boundary_data: Dict,
        features: Dict,
        criteria: Dict,
        ahp_results: Dict,
        ml_results: Dict,
        final_scores: Dict
    ) -> Dict:
        """Compile all results into final output"""
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
            'key_insights': self._generate_insights(features, final_scores)
        }
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID"""
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"LAND_{timestamp}_{unique_id}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_insights(self, features: Dict, scores: Dict) -> Dict:
        """Generate key insights from analysis"""
        insights = {
            'strengths': [],
            'concerns': [],
            'opportunities': []
        }
        
        # Analyze terrain
        terrain = features.get('terrain', {})
        if terrain.get('slope_avg', 999) < 5:
            insights['strengths'].append(
                f"Gentle slope ({terrain.get('slope_avg', 0):.1f}°) ideal for construction"
            )
        elif terrain.get('slope_avg', 0) > 15:
            insights['concerns'].append(
                f"Steep slope ({terrain.get('slope_avg', 0):.1f}°) may increase development costs"
            )
        
        # Analyze infrastructure
        infra = features.get('infrastructure', {})
        road_dist = infra.get('nearest_road_distance', 999999)
        if road_dist < 500:
            insights['strengths'].append(
                f"Excellent road access (only {road_dist:.0f}m away)"
            )
        elif road_dist > 2000:
            insights['concerns'].append(
                f"Limited road access ({road_dist/1000:.1f}km to nearest road)"
            )
        
        # Analyze environmental factors
        env = features.get('environmental', {})
        flood_risk = env.get('flood_risk_percent', 0)
        if flood_risk > 30:
            insights['concerns'].append(
                f"High flood risk in {flood_risk:.0f}% of area"
            )
        elif flood_risk < 10:
            insights['strengths'].append(
                "Low flood risk throughout the property"
            )
        
        # Add opportunities based on scores
        top_rec = scores.get('recommendations', [{}])[0] if scores.get('recommendations') else {}
        if top_rec.get('suitability_score', 0) > 8:
            insights['opportunities'].append(
                f"Excellent potential for {top_rec.get('usage_type', 'development')}"
            )
        
        return insights
