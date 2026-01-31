# ============================================================================
# FILE: intelligence/spatial/__init__.py
# Spatial Intelligence Module
# ============================================================================

"""
Spatial intelligence and analysis modules

This package contains spatial analysis tools including:
- Suitability grid analysis
- Heatmap generation
- Spatial clustering
- Location optimization
"""

from .suitability_grid import SuitabilityGridAnalyzer

__all__ = [
    'SuitabilityGridAnalyzer'
]

__version__ = '1.0.0'
