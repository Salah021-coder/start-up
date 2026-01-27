# ============================================================================
# FILE: ui/pages/home.py (ADD HEATMAP FEATURE)
# ============================================================================

import streamlit as st

def render():
    """Render home page"""
    
    # Hero section
    st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <h1 style='font-size: 3rem; margin-bottom: 1rem;'>
                🌍 Land Evaluation AI
            </h1>
            <p style='font-size: 1.5rem; color: #666; margin-bottom: 2rem;'>
                AI-powered land analysis for real estate professionals
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start New Analysis", use_container_width=True, type="primary"):
            st.session_state.current_page = 'analysis'
            st.rerun()
    
    st.markdown("---")
    
    # Features
    st.markdown("### How It Works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            #### 1️⃣ Define Area
            - Draw boundaries on map
            - Upload KML, GeoJSON
            - Up to 100 km²
        """)
    
    with col2:
        st.markdown("""
            #### 2️⃣ AI Analysis
            - Auto criteria selection
            - Earth Engine data
            - AHP + ML models
        """)
    
    with col3:
        st.markdown("""
            #### 3️⃣ Get Results
            - Suitability scores
            - 40+ recommendations
            - Detailed insights
        """)
    
    with col4:
        st.markdown("""
            #### 4️⃣ Heatmap 🆕
            - **Find best spots**
            - **Visual heatmap**
            - **Top 5 locations**
        """)
    
    st.markdown("---")
    
    # NEW: Heatmap Feature Highlight
    st.markdown("### 🆕 New Feature: Suitability Heatmap")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Discover the best locations within your land!**
        
        Our new heatmap feature analyzes your entire property and shows you:
        - 🎯 **Top 5 best locations** for your chosen development type
        - 🗺️ **Visual heatmap** with color-coded suitability
        - 📊 **Detailed scores** for every point analyzed
        - 💡 **Smart recommendations** for optimal placement
        
        Perfect for:
        - Finding the best spot for a house on large property
        - Identifying optimal areas for commercial development
        - Locating ideal zones for agricultural activities
        - Discovering premium locations for luxury villas
        """)
    
    with col2:
        st.info("""
        **How it works:**
        
        1. Define your area
        2. Choose land use type
        3. Set grid resolution
        4. View heatmap
        5. Get top locations!
        
        ⏱️ Takes 1-2 minutes
        📍 Analyzes 20-200 points
        """)
    
    st.markdown("---")
    
    # Technologies
    st.markdown("### Powered By Advanced Technologies")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("**Google Earth Engine**\n\nSatellite imagery\nTerrain data\nClimate info")
    
    with col2:
        st.success("**AHP Algorithm**\n\nMulti-criteria\ndecision analysis\nWeighted scoring")
    
    with col3:
        st.warning("**Machine Learning**\n\nPattern recognition\nPredictive models\nRisk assessment")
    
    with col4:
        st.error("**Gemini AI**\n\nInteractive chat\nExplain results\nAnswer questions")
    
    # Sample results
    st.markdown("---")
    st.markdown("### Sample Analysis Results")
    
    with st.expander("View Sample Report"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Score", "8.2/10", "+1.5")
        with col2:
            st.metric("Confidence", "87%", "+5%")
        with col3:
            st.metric("Top Use", "Residential")
        
        st.markdown("""
        **Key Findings:**
        - ✅ Gentle slope (4.2°) ideal for construction
        - ✅ Excellent road access (450m)
        - ✅ All utilities available
        - 🗺️ **Heatmap shows 3 premium zones for building**
        - ⚠️ Minor flood risk in 5% of area
        """)
