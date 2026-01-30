from typing import Dict, Optional
import json

class PromptBuilder:
    """Build context-aware prompts for Gemini"""
    
    @staticmethod
    def build_system_prompt(analysis_results: Optional[Dict] = None) -> str:
        """Build system prompt with analysis context"""
        
        base_prompt = """You are an expert land evaluation assistant specializing in real estate analysis.

Your role is to help users understand their land analysis results, including:
- Terrain and topographic data (slope, elevation, aspect)
- Soil characteristics and fertility  
- Environmental factors (flood risk, vegetation, NDVI)
- Infrastructure proximity and accessibility
- AHP (Analytic Hierarchy Process) methodology
- Machine learning predictions
- Land use recommendations

Guidelines:
- Provide clear, concise explanations
- Use accessible language, avoiding unnecessary jargon
- Reference specific data from the analysis when available
- Be helpful but honest about limitations
- Suggest practical next steps when appropriate
- Use bullet points for lists, but keep responses conversational

Always maintain a professional, friendly tone."""

        if analysis_results:
            context = f"""

CURRENT ANALYSIS CONTEXT:
{json.dumps(analysis_results, indent=2)}

Use this information to provide context-aware, specific responses."""
            return base_prompt + context
        
        return base_prompt
    
    @staticmethod
    def build_quick_answer_prompt(question: str, context: Dict) -> str:
        """Build prompt for quick predefined questions"""
        return f"""Based on the current analysis results, answer this question clearly and specifically:

Question: {question}

Analysis Context:
{json.dumps(context, indent=2)}

Provide a direct, helpful answer referencing the actual data."""


# ============================================================================
# FILE: ai/context/analysis_context.py
# ============================================================================

from typing import Dict, Any

class AnalysisContextFormatter:
    """Format analysis results for chatbot context"""
    
    @staticmethod
    def format_for_chat(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format complex analysis results for chatbot"""
        if not analysis_results:
            return {}
        
        return {
            'location': {
                'coordinates': analysis_results.get('boundary', {}).get('centroid'),
                'area_hectares': analysis_results.get('boundary', {}).get('area_hectares'),
                'area_acres': analysis_results.get('boundary', {}).get('area_acres'),
            },
            'scores': {
                'overall': analysis_results.get('overall_score'),
                'confidence': analysis_results.get('confidence_level'),
                'ahp_score': analysis_results.get('final_scores', {}).get('ahp_score'),
                'ml_score': analysis_results.get('final_scores', {}).get('ml_score'),
            },
            'recommendations': analysis_results.get('recommendations', []),
            'insights': analysis_results.get('key_insights', {}),
            'features': {
                'terrain': analysis_results.get('features', {}).get('terrain', {}),
                'environmental': analysis_results.get('features', {}).get('environmental', {}),
                'infrastructure': analysis_results.get('features', {}).get('infrastructure', {})
            }
        }

