# ============================================================================
# FILE: app.py (UPDATED WITH PROPER RISK ASSESSMENT INTEGRATION)
# ============================================================================

import streamlit as st
from ui.pages import home, analysis, results, history
from ui.components.chatbot_widget import render_chatbot
from utils.ee_manager import EarthEngineManager
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import risk_analysis page
try:
    from ui.pages import risk_analysis
    HAS_RISK_ANALYSIS = True
except ImportError:
    HAS_RISK_ANALYSIS = False
    print("⚠️  Risk analysis page not found")

# Import heatmap page
try:
    from ui.pages import heatmap
    HAS_HEATMAP = True
except ImportError:
    HAS_HEATMAP = False
    print("⚠️  Heatmap page not found")

# Page configuration
st.set_page_config(
    page_title="LandSense",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Earth Engine on startup
@st.cache_resource
def init_earth_engine():
    """Initialize Earth Engine (cached)"""
    return EarthEngineManager.initialize()

# Try to initialize EE
ee_available = init_earth_engine()

# Show warning if EE not available
if not ee_available:
    st.warning("""
        ⚠️ **Google Earth Engine not configured**
        
        Some features may have limited functionality. To enable full analysis:
        1. Configure GEE_SERVICE_ACCOUNT_JSON in Streamlit secrets
        2. Or authenticate locally: `earthengine authenticate`
    """)

# Custom CSS
css_path = 'ui/styles/custom.css'
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'boundary_data' not in st.session_state:
        st.session_state.boundary_data = None
    if 'analysis_id' not in st.session_state:
        st.session_state.analysis_id = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_initialized' not in st.session_state:
        st.session_state.chat_initialized = False
    if 'ee_available' not in st.session_state:
        st.session_state.ee_available = ee_available
    if 'heatmap_results' not in st.session_state:
        st.session_state.heatmap_results = None

def main():
    """Main application logic"""
    initialize_session_state()
    
    # Render chatbot in sidebar (always available)
    render_chatbot(st.session_state.analysis_results)
    
    # Navigation menu
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📍 Navigation")
        
        # Home button
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
        
        # New Analysis button
        if st.button("🗺️ New Analysis", use_container_width=True):
            st.session_state.current_page = 'analysis'
            st.rerun()
        
        # Show results button if analysis exists
        if st.session_state.analysis_results:
            if st.button("📊 View Results", use_container_width=True):
                st.session_state.current_page = 'results'
                st.rerun()
            
            # Risk Analysis button (only show if analysis exists AND page is available)
            if HAS_RISK_ANALYSIS:
                if st.button(
                    "🛡️ Risk Assessment",
                    use_container_width=True,
                    help="Detailed comprehensive risk analysis"
                ):
                    st.session_state.current_page = 'risk_analysis'
                    st.rerun()
            else:
                # Show disabled button with tooltip
                st.button(
                    "🛡️ Risk Assessment",
                    use_container_width=True,
                    disabled=True,
                    help="Risk analysis page not available"
                )
        
        # Heatmap button (show if boundary exists AND page available)
        if st.session_state.boundary_data and HAS_HEATMAP:
            if st.button(
                "🗺️ Suitability Heatmap",
                use_container_width=True,
                help="Find the best locations within your area"
            ):
                st.session_state.current_page = 'heatmap'
                st.rerun()
        
        # History button
        if st.button("📜 History", use_container_width=True):
            st.session_state.current_page = 'history'
            st.rerun()
        
        # Show EE status
        st.markdown("---")
        if st.session_state.ee_available:
            st.success("✅ Earth Engine Ready")
        else:
            st.error("❌ Earth Engine Offline")
        
        # Show feature availability
        st.markdown("---")
        st.markdown("### 🔧 Features")
        st.markdown(f"{'✅' if HAS_RISK_ANALYSIS else '❌'} Risk Assessment")
        st.markdown(f"{'✅' if HAS_HEATMAP else '❌'} Suitability Heatmap")
    
    # Render current page
    current_page = st.session_state.current_page
    
    try:
        if current_page == 'home':
            home.render()
        
        elif current_page == 'analysis':
            analysis.render()
        
        elif current_page == 'results':
            results.render()
        
        elif current_page == 'risk_analysis':
            if HAS_RISK_ANALYSIS:
                risk_analysis.render()
            else:
                st.error("❌ Risk analysis page not available")
                st.info("The risk_analysis.py file may be missing or have import errors.")
                if st.button("Return to Home"):
                    st.session_state.current_page = 'home'
                    st.rerun()
        
        elif current_page == 'heatmap':
            if HAS_HEATMAP:
                heatmap.render()
            else:
                st.error("❌ Heatmap page not available")
                st.info("The heatmap.py file may be missing or have import errors.")
                if st.button("Return to Home"):
                    st.session_state.current_page = 'home'
                    st.rerun()
        
        elif current_page == 'history':
            history.render()
        
        else:
            st.error(f"Unknown page: {current_page}")
            if st.button("Return to Home"):
                st.session_state.current_page = 'home'
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error rendering page '{current_page}': {str(e)}")
        
        with st.expander("Show Error Details"):
            import traceback
            st.code(traceback.format_exc())
        
        if st.button("Return to Home"):
            st.session_state.current_page = 'home'
            st.rerun()

if __name__ == "__main__":
    main()
