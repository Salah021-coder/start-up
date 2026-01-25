# ============================================================================
# FILE: config/gemini_config.py (STREAMLIT CLOUD COMPATIBLE)
# ============================================================================

import os
from typing import Dict

class GeminiConfig:
    """Gemini AI Configuration - Works locally and on Streamlit Cloud"""
    
    MODEL_NAME = 'gemini-2.5-pro'
    
    # Generation Configuration
    TEMPERATURE = 0.7
    MAX_OUTPUT_TOKENS = 2048
    TOP_P = 0.95
    TOP_K = 40
    
    # Safety Settings
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]
    
    # System Prompts
    BASE_SYSTEM_PROMPT = """You are an expert land evaluation assistant specializing in real estate analysis.

Your role is to help users understand their land analysis results, including:
- Terrain and topographic data (slope, elevation, aspect)
- Soil characteristics and fertility
- Environmental factors (flood risk, vegetation)
- Infrastructure proximity and accessibility
- AHP (Analytic Hierarchy Process) scoring methodology
- Machine learning predictions for land suitability
- Land use recommendations

Guidelines:
- Provide clear, concise explanations
- Use accessible language, avoiding unnecessary jargon
- Reference specific data from the analysis when available
- Be helpful but honest about limitations
- Suggest practical next steps when appropriate

Always maintain a professional, friendly tone."""

    @staticmethod
    def get_api_key():
        """Fetch API key from Streamlit secrets or environment variable"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'gemini' in st.secrets:
                return st.secrets["gemini"]["api_key"]
        except Exception:
            pass
        return os.getenv("GEMINI_API_KEY")

    @classmethod
    def get_generation_config(cls) -> Dict:
        return {
            'temperature': cls.TEMPERATURE,
            'max_output_tokens': cls.MAX_OUTPUT_TOKENS,
            'top_p': cls.TOP_P,
            'top_k': cls.TOP_K,
        }
