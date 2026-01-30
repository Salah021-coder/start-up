# ============================================================================
# FILE: config/gemini_config.py
# ============================================================================

import os
from typing import Dict

class GeminiConfig:
    """Gemini AI Configuration (Streamlit + Local)"""

    MODEL_NAME = "gemini-2.5-flash"

    TEMPERATURE = 0.7
    MAX_OUTPUT_TOKENS = 2048
    TOP_P = 0.95
    TOP_K = 40

    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    @classmethod
    def get_api_key(cls) -> str:
        """Load API key from Streamlit secrets or env var"""
        try:
            import streamlit as st
            if "gemini" in st.secrets:
                return st.secrets["gemini"]["api_key"]
        except Exception:
            pass

        return os.getenv("GEMINI_API_KEY")

    @classmethod
    def get_generation_config(cls) -> Dict:
        return {
            "temperature": cls.TEMPERATURE,
            "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
            "top_p": cls.TOP_P,
            "top_k": cls.TOP_K,
        }
