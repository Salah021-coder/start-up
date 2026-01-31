# ============================================================================
# FILE: ui/pages/__init__.py (FIXED)
# UI Pages Module
# ============================================================================

"""
Streamlit page modules

Contains all UI pages:
- Home page
- Analysis page
- Results page
- History page
- Risk analysis page (comprehensive risk assessment)
- Heatmap page
"""

# Import all page modules
from . import home
from . import analysis
from . import results
from . import history

# Import risk_analysis if it exists, otherwise skip
try:
    from . import risk_analysis
    HAS_RISK_ANALYSIS = True
except ImportError:
    risk_analysis = None
    HAS_RISK_ANALYSIS = False

# Import heatmap if it exists, otherwise skip
try:
    from . import heatmap
    HAS_HEATMAP = True
except ImportError:
    heatmap = None
    HAS_HEATMAP = False

__all__ = [
    'home',
    'analysis',
    'results',
    'history',
    'risk_analysis',
    'heatmap',
    'HAS_RISK_ANALYSIS',
    'HAS_HEATMAP'
]
