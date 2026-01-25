# ============================================================================
# FILE: app.py (UPDATED WITH PROPER EE INITIALIZATION)
# ============================================================================

import streamlit as st
from ui.pages import home, analysis, results, history
from ui.components.chatbot_widget import render_chatbot
from utils.ee_manager import EarthEngineManager
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Page configuration
st.set_page_config(
    page_title="Land Evaluation AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Earth Engine on startup (only once)
@st.cache_resource
def init_earth_engine():
    """Initialize Earth Engine (cached to run only once)"""
    print("\n" + "="*60)
    print("Initializing Earth Engine...")
    print("="*60)
    result = EarthEngineManager.initialize()
    if result:
        print("✅ Earth Engine is ready!")
    else:
        print("❌ Earth Engine initialization failed")
    print("="*60 + "\n")
    return result

# Try to initialize EE
ee_available = init_earth_engine()

# Load custom CSS
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

def main():
    """Main application logic"""
    initialize_session_state()
    
    # Show EE status warning if not available
    if not st.session_state.ee_available:
        st.error("""
            ❌ **Google Earth Engine Not Configured**
            
            Earth Engine is required for land analysis. Please follow these steps:
            
            1. **Install**: `pip install earthengine-api`
            2. **Authenticate**: `earthengine authenticate`
            3. **Restart** this app
            
            The app will work with limited functionality until Earth Engine is configured.
        """)
        
        with st.expander("📖 Detailed Setup Instructions"):
            st.markdown("""
            ### Step-by-Step Setup:
            
            **1. Open Terminal/Command Prompt:**
```bash
            cd F:\\VS_CODE\\startup_app\\land-evaluation-mvp
            venv\\Scripts\\activate
```
            
            **2. Install Earth Engine:**
```bash
            pip install earthengine-api
```
            
            **3. Authenticate (this opens your browser):**
```bash
            earthengine authenticate
```
            
            **4. Sign in** with your Google account
            
            **5. Restart** this Streamlit app
            
            **6. Test** by running: `python test_ee.py`
            """)
    
    # Render chatbot in sidebar (always available)
    render_chatbot(st.session_state.analysis_results)
    
    # Navigation menu
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📍 Navigation")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
        
        if st.button("🗺️ New Analysis", use_container_width=True):
            st.session_state.current_page = 'analysis'
            st.rerun()
        
        if st.session_state.analysis_results:
            if st.button("📊 View Results", use_container_width=True):
                st.session_state.current_page = 'results'
                st.rerun()
        
        if st.button("📜 History", use_container_width=True):
            st.session_state.current_page = 'history'
            st.rerun()
        
        # Show EE status indicator
        st.markdown("---")
        st.markdown("### 🛰️ Earth Engine")
        if st.session_state.ee_available:
            st.success("✅ Connected")
        else:
            st.error("❌ Not Configured")
            if st.button("📖 Setup Guide", use_container_width=True):
                st.session_state.show_ee_guide = True
    
    # Render current page
    if st.session_state.current_page == 'home':
        home.render()
    elif st.session_state.current_page == 'analysis':
        analysis.render()
    elif st.session_state.current_page == 'results':
        results.render()
    elif st.session_state.current_page == 'history':
        history.render()

if __name__ == "__main__":
    main()
