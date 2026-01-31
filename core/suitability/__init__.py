# ============================================================================
# FILE: core/suitability/__init__.py
# Suitability Analysis Module
# ============================================================================

"""
Suitability analysis and scoring modules

Contains:
- AHP (Analytic Hierarchy Process) engine
- Multi-criteria decision analysis
- Scoring algorithms
"""

from .ahp_engine import AHPEngine

__all__ = [
    'AHPEngine'
]

__version__ = '1.0.0'
