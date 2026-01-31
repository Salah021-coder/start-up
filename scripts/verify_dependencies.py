# ============================================================================
# FILE: scripts/verify_dependencies.py
# Verify All Required Dependencies Are Installed
# ============================================================================

"""
Verify that all required dependencies are properly installed

Usage:
    python scripts/verify_dependencies.py
"""

import sys


def check_dependencies():
    """Check all required dependencies"""
    
    print("=" * 70)
    print("VERIFYING DEPENDENCIES")
    print("=" * 70 + "\n")
    
    dependencies = {
        # Core
        'streamlit': 'Streamlit (UI framework)',
        'pandas': 'Pandas (data processing)',
        'numpy': 'NumPy (numerical computing)',
        
        # Geospatial
        'shapely': 'Shapely (geometry operations)',
        'geopandas': 'GeoPandas (geospatial data)',
        'pyproj': 'PyProj (coordinate transformations)',
        'folium': 'Folium (interactive maps)',
        'streamlit_folium': 'Streamlit-Folium (Folium integration)',
        
        # Google Earth Engine
        'ee': 'Earth Engine Python API',
        
        # Data fetching
        'requests': 'Requests (HTTP library)',
        
        # Visualization
        'plotly': 'Plotly (interactive charts)',
        'matplotlib': 'Matplotlib (plotting)',
        
        # AI
        'google.generativeai': 'Google Generative AI (Gemini)',
        
        # ML (optional)
        'sklearn': 'Scikit-learn (ML library)',
    }
    
    missing = []
    installed = []
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            installed.append((module, description))
            print(f"✓ {description}")
        except ImportError:
            missing.append((module, description))
            print(f"✗ {description} - NOT FOUND")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Installed: {len(installed)}/{len(dependencies)}")
    print(f"Missing: {len(missing)}/{len(dependencies)}")
    
    if missing:
        print("\n⚠️  MISSING DEPENDENCIES:")
        for module, description in missing:
            print(f"  - {module}: {description}")
        
        print("\nInstall missing dependencies with:")
        print("  pip install -r requirements.txt")
        
        return False
    else:
        print("\n✓ All dependencies are installed!")
        return True


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
