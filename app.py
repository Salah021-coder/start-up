# app.py

import os
import sys
import streamlit as st

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.ee_manager import EarthEngineManager
from ui.pages import home, analysis, results, history
from ui.components.chatbot_widget import render_chatbot


# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Land Evaluation AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------------
# Earth Engine initialization (RUNS ONCE)
# ------------------------------------------------------------------
@st.cache_resource
def init_earth_engine():
    return EarthEngineManager.initialize()


ee_available = init_earth_engine()


# ------------------------------------------------------------------
# Session state initialization
# ------------------------------------------------------------------
def initialize_session_state():
    defaults = {
        "current_page": "home",
        "analysis_results": None,
        "boundary_data": None,
        "analysis_id": None,
        "chat_messages": [],
        "chat_initialized": False,
        "ee_available": ee_available,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ------------------------------------------------------------------
# Main app
# ------------------------------------------------------------------
def main():
    initialize_session_state()

    # EE status banner (truthful, cloud-safe)
    if not st.session_state.ee_available:
        st.error(
            """
            ❌ **Google Earth Engine not available**

            This app runs on **Streamlit Cloud** and requires:
            • A valid **service account**
            • Correct **Streamlit Secrets**
            • Earth Engine access granted to the service account

            ❗ `earthengine authenticate` is NOT used on Streamlit Cloud.
            """
        )

    # Sidebar chatbot (always visible)
    render_chatbot(st.session_state.analysis_results)

    # ------------------------------------------------------------------
    # Sidebar navigation
    # ------------------------------------------------------------------
    with st.sidebar:
        st.markdown("## 📍 Navigation")

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

        if st.button("🗺️ New Analysis", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()

        if st.session_state.analysis_results:
            if st.button("📊 Results", use_container_width=True):
                st.session_state.current_page = "results"
                st.rerun()

        if st.button("📜 History", use_container_width=True):
            st.session_state.current_page = "history"
            st.rerun()

        st.markdown("---")
        st.markdown("### 🛰️ Earth Engine Status")

        if st.session_state.ee_available:
            st.success("✅ Connected")
        else:
            st.error("❌ Not connected")

    # ------------------------------------------------------------------
    # Page rendering
    # ------------------------------------------------------------------
    if st.session_state.current_page == "home":
        home.render()

    elif st.session_state.current_page == "analysis":
        analysis.render()

    elif st.session_state.current_page == "results":
        results.render()

    elif st.session_state.current_page == "history":
        history.render()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()
