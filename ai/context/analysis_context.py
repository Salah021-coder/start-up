"""
Format Analysis Results for Chatbot Context
"""
from typing import Dict, Any

class AnalysisContextFormatter:
    @staticmethod
    def format_for_chat(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format complex analysis results for chatbot consumption"""
        return {
            'location': {
                'coordinates': analysis_results.get('boundary_centroid'),
                'area_hectares': analysis_results.get('area_hectares'),
                'area_acres': analysis_results.get('area_acres'),
            },
            'scores': {
                'overall': analysis_results.get('overall_score'),
                'confidence': analysis_results.get('confidence_level'),
                'criteria_breakdown': analysis_results.get('criteria_scores', {})
            },
            'recommendations': [
                {
                    'rank': i + 1,
                    'usage': rec['usage_type'],
                    'score': rec['suitability_score'],
                    'key_factors': rec['supporting_factors']
                }
                for i, rec in enumerate(analysis_results.get('recommendations', []))
            ],
            'insights': {
                'strengths': analysis_results.get('key_strengths', []),
                'concerns': analysis_results.get('concerns', []),
                'opportunities': analysis_results.get('opportunities', [])
            },
            'environmental': {
                'slope_avg': analysis_results.get('terrain', {}).get('slope_avg'),
                'elevation_range': analysis_results.get('terrain', {}).get('elevation_range'),
                'ndvi_avg': analysis_results.get('vegetation', {}).get('ndvi_avg'),
                'flood_risk': analysis_results.get('environmental', {}).get('flood_risk')
            },
            'infrastructure': {
                'nearest_road': analysis_results.get('infrastructure', {}).get('road_distance'),
                'utilities_available': analysis_results.get('infrastructure', {}).get('utilities')
            }
        }
    
    @staticmethod
    def get_relevant_context(query: str, full_context: Dict) -> Dict:
        """Extract only relevant context based on user query"""
        query_lower = query.lower()
        
        relevant = {}
        
        # Keywords mapping
        if any(word in query_lower for word in ['slope', 'terrain', 'elevation', 'topography']):
            relevant['environmental'] = full_context.get('environmental', {})
        
        if any(word in query_lower for word in ['score', 'rating', 'overall']):
            relevant['scores'] = full_context.get('scores', {})
        
        if any(word in query_lower for word in ['recommend', 'usage', 'best use']):
            relevant['recommendations'] = full_context.get('recommendations', [])
        
        if any(word in query_lower for word in ['road', 'utility', 'infrastructure']):
            relevant['infrastructure'] = full_context.get('infrastructure', {})
        
        # Always include basic info
        relevant['location'] = full_context.get('location', {})
        
        return relevant
