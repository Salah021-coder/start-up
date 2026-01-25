import numpy as np
from typing import Dict
from sklearn.ensemble import RandomForestRegressor
import joblib
from pathlib import Path

class SuitabilityPredictor:
    """ML-based land suitability predictor"""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load pre-trained model or create new one"""
        model_path = Path('intelligence/ml/pretrained/suitability_model.joblib')
        
        if model_path.exists():
            self.model = joblib.load(model_path)
            self.is_trained = True
        else:
            # Create new model with default parameters
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            # In production, this would be trained on real data
            self.is_trained = False
    
    def predict(self, features: Dict) -> Dict:
        """
        Predict land suitability scores
        """
        # Extract features for prediction
        feature_vector = self._extract_feature_vector(features)
        
        if self.is_trained:
            # Use trained model
            predictions = self.model.predict([feature_vector])
            score = float(predictions[0])
        else:
            # Use rule-based fallback
            score = self._rule_based_prediction(features)
        
        # Calculate confidence
        confidence = self._calculate_confidence(features)
        
        return {
            'suitability_score': score,
            'confidence': confidence,
            'methodology': 'ML' if self.is_trained else 'rule-based',
            'feature_importance': self._get_feature_importance() if self.is_trained else {}
        }
    
    def _extract_feature_vector(self, features: Dict) -> np.ndarray:
        """Extract features into vector for ML model"""
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        vector = [
            terrain.get('slope_avg', 0),
            terrain.get('elevation_avg', 0),
            env.get('ndvi_avg', 0.5),
            env.get('flood_risk_percent', 0),
            infra.get('nearest_road_distance', 1000),
            len(infra.get('utilities_available', {})),
            terrain.get('buildability_score', 5),
            env.get('environmental_score', 5)
        ]
        
        return np.array(vector)
    
    def _rule_based_prediction(self, features: Dict) -> float:
        """Fallback rule-based prediction"""
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        score = 5.0  # Base score
        
        # Terrain factors
        score += terrain.get('buildability_score', 5) * 0.3
        
        # Environmental factors
        score += env.get('environmental_score', 5) * 0.3
        
        # Infrastructure factors
        score += infra.get('infrastructure_score', 5) * 0.4
        
        return min(10, max(0, score))
    
    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate prediction confidence"""
        # Base confidence
        confidence = 0.7
        
        # Increase confidence if we have complete data
        if all(key in features for key in ['terrain', 'environmental', 'infrastructure']):
            confidence += 0.2
        
        # Increase if model is trained
        if self.is_trained:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _get_feature_importance(self) -> Dict:
        """Get feature importance from trained model"""
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        feature_names = ['slope', 'elevation', 'ndvi', 'flood_risk', 
                        'road_distance', 'utilities', 'buildability', 'env_score']
        
        return {name: float(imp) for name, imp in zip(feature_names, importances)}