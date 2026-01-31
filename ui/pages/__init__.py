# ============================================================================
# FILE: ui/pages/__init__.py
# UI Pages Module
# ============================================================================

"""
Streamlit page modules

Contains all UI pages:
- Home page
- Analysis page
- Results page
- History page
- Risk analysis page
- Heatmap page
"""

from . import home
from . import analysis
from . import results
from . import history
from . import risk_analysis
from . import heatmap

__all__ = [
    'home',
    'analysis',
    'results',
    'history',
    'risk_analysis',
    'heatmap'
]
