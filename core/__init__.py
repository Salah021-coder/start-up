# ============================================================================
# FILE: core/features/__init__.py
# Feature Extraction Module
# ============================================================================

"""
Feature extraction modules for land analysis

This package contains extractors for:
- Terrain features (slope, elevation, aspect)
- Environmental features (vegetation, land cover, water)
- Infrastructure features (roads, amenities, utilities)
"""

from .terrain import TerrainExtractor
from .environmental import EnvironmentalExtractor
from .infrastructure import InfrastructureExtractor

__all__ = [
    'TerrainExtractor',
    'EnvironmentalExtractor',
    'InfrastructureExtractor'
]

__version__ = '1.0.0'
