# ============================================================================
# FILE: core/recommendation/__init__.py
# Recommendation Engine Module
# ============================================================================

"""
Land-use recommendation generation

Contains:
- Usage recommender
- Report generators
- Recommendation scoring
"""

from .usage_recommender import UsageRecommender

__all__ = [
    'UsageRecommender'
]

__version__ = '1.0.0'
