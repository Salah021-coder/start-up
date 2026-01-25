import numpy as np
from typing import Dict, List

class AHPSolver:
    """Analytic Hierarchy Process Solver"""
    
    def __init__(self):
        self.consistency_threshold = 0.1  # CR < 0.1 is acceptable
    
    def solve(self, features: Dict, criteria: Dict) -> Dict:
        """
        Solve AHP problem
        Returns weighted scores for each criterion
        """
        
        # Build pairwise comparison matrix
        matrix = self._build_comparison_matrix(criteria)
        
        # Calculate priority vector (weights)
        weights = self._calculate_weights(matrix)
        
        # Check consistency
        cr = self._check_consistency(matrix, weights)
        
        # Score each criterion
        criterion_scores = self._score_criteria(features, criteria)
        
        # Calculate weighted total
        total_score = self._calculate_total_score(criterion_scores, weights)
        
        return {
            'weights': weights,
            'consistency_ratio': cr,
            'is_consistent': cr < self.consistency_threshold,
            'criterion_scores': criterion_scores,
            'total_score': total_score,
            'methodology': 'AHP'
        }
    
    def _build_comparison_matrix(self, criteria: Dict) -> np.ndarray:
        """Build pairwise comparison matrix from criteria weights"""
        flat_criteria = self._flatten_criteria(criteria)
        n = len(flat_criteria)
        matrix = np.ones((n, n))
        
        weights_list = list(flat_criteria.values())
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Comparison based on weight ratio
                    ratio = weights_list[i] / weights_list[j]
                    matrix[i][j] = ratio
        
        return matrix
    
    def _calculate_weights(self, matrix: np.ndarray) -> Dict:
        """Calculate priority vector using eigenvalue method"""
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        max_index = np.argmax(eigenvalues)
        principal_eigenvector = np.real(eigenvectors[:, max_index])
        
        # Normalize
        weights = principal_eigenvector / np.sum(principal_eigenvector)
        
        return {f"criterion_{i}": float(w) for i, w in enumerate(weights)}
    
    def _check_consistency(self, matrix: np.ndarray, weights: Dict) -> float:
        """Calculate Consistency Ratio"""
        n = matrix.shape[0]
        
        # Calculate lambda_max
        weighted_sum = matrix @ np.array(list(weights.values()))
        lambda_max = np.mean(weighted_sum / np.array(list(weights.values())))
        
        # Calculate CI
        ci = (lambda_max - n) / (n - 1)
        
        # Random Index (RI) for different matrix sizes
        ri_values = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 
                     7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        ri = ri_values.get(n, 1.49)
        
        # Calculate CR
        cr = ci / ri if ri != 0 else 0
        
        return cr
    
    def _score_criteria(self, features: Dict, criteria: Dict) -> Dict:
        """Score each criterion based on features"""
        scores = {}
        
        terrain = features.get('terrain', {})
        env = features.get('environmental', {})
        infra = features.get('infrastructure', {})
        
        # Score terrain criteria
        if 'terrain' in criteria:
            scores['terrain_slope'] = self._score_slope(terrain.get('slope_avg', 0))
            scores['terrain_elevation'] = self._score_elevation(terrain.get('elevation_avg', 0))
        
        # Score environmental criteria
        if 'environmental' in criteria:
            scores['env_flood_risk'] = self._score_flood_risk(
                env.get('flood_risk_percent', 0)
            )
            scores['env_vegetation'] = env.get('ndvi_avg', 0.5) * 10
        
        # Score infrastructure criteria
        if 'infrastructure' in criteria:
            scores['infra_road'] = infra.get('accessibility_score', 5)
            scores['infra_utilities'] = infra.get('infrastructure_score', 5)
        
        return scores
    
    def _score_slope(self, slope: float) -> float:
        """Score slope (lower is better for most uses)"""
        if slope < 3:
            return 10
        elif slope < 8:
            return 8
        elif slope < 15:
            return 6
        elif slope < 30:
            return 4
        else:
            return 2
    
    def _score_elevation(self, elevation: float) -> float:
        """Score elevation (moderate is often best)"""
        if 100 <= elevation <= 500:
            return 9
        elif 50 <= elevation <= 1000:
            return 7
        else:
            return 5
    
    def _score_flood_risk(self, risk_percent: float) -> float:
        """Score flood risk (lower is better)"""
        return max(0, 10 - (risk_percent / 10))
    
    def _calculate_total_score(self, scores: Dict, weights: Dict) -> float:
        """Calculate weighted total score"""
        total = 0
        weight_sum = 0
        
        for i, (criterion, score) in enumerate(scores.items()):
            weight = weights.get(f"criterion_{i}", 0)
            total += score * weight
            weight_sum += weight
        
        return total / weight_sum if weight_sum > 0 else 5.0
    
    def _flatten_criteria(self, criteria: Dict) -> Dict:
        """Flatten nested criteria dictionary"""
        flat = {}
        for category, items in criteria.items():
            for criterion, weight in items.items():
                key = f"{category}_{criterion}"
                flat[key] = weight
        return flat