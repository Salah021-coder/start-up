# ============================================================================
# FILE: ui/pages/heatmap.py (NEW FILE)
# ============================================================================

import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd

def render():
    """Render suitability heatmap page"""
    
    st.title("🗺️ Suitability Heatmap Analysis")
    
    st.markdown("""
    Discover the **best locations** within your land area for specific uses.
    The system analyzes multiple points across your property and creates a heatmap
    showing where development would be most suitable.
    """)
    
    # Check if boundary is available
    if not st.session_state.get('boundary_data'):
        st.warning("⚠️ Please define a boundary first")
        if st.button("Go to Analysis Page"):
            st.session_state.current_page = 'analysis'
            st.rerun()
        return
    
    boundary_data = st.session_state.boundary_data
    
    # Land use selection
    st.markdown("### Select Land Use Type")
    
    land_use_options = {
        'Residential Development': 'residential',
        'Commercial Development': 'commercial',
        'Agricultural Use': 'agricultural',
        'Solar Farm': 'solar_farm',
        'Tourism/Recreation': 'tourism',
        'Industrial': 'industrial'
    }
    
    selected_use = st.selectbox(
        "What type of development are you planning?",
        list(land_use_options.keys())
    )
    
    land_use_type = land_use_options[selected_use]
    
    # Grid resolution
    col1, col2 = st.columns(2)
    
    with col1:
        grid_size = st.slider(
            "Grid Resolution (meters)",
            min_value=50,
            max_value=500,
            value=100,
            step=50,
            help="Smaller values = more detail but slower analysis"
        )
    
    with col2:
        max_points = st.slider(
            "Maximum Analysis Points",
            min_value=20,
            max_value=200,
            value=100,
            step=20,
            help="More points = more accurate but slower"
        )
    
    # Run analysis button
    if st.button("🔍 Analyze Suitability Across Area", type="primary", use_container_width=True):
        run_heatmap_analysis(boundary_data, land_use_type, grid_size, max_points)
    
    # Show results if available
    if st.session_state.get('heatmap_results'):
        render_heatmap_results(st.session_state.heatmap_results)


def run_heatmap_analysis(boundary_data, land_use_type, grid_size, max_points):
    """Run the heatmap analysis"""
    
    with st.spinner("🔍 Analyzing suitability across your land... This may take 1-2 minutes..."):
        try:
            from intelligence.spatial.suitability_grid import SuitabilityGridAnalyzer
            
            # Create analyzer
            analyzer = SuitabilityGridAnalyzer(grid_size_meters=grid_size)
            
            # Run analysis
            results = analyzer.analyze_area(
                boundary_geometry=boundary_data['geometry'],
                land_use_type=land_use_type,
                max_points=max_points
            )
            
            # Store results
            st.session_state.heatmap_results = results
            
            st.success("✅ Analysis complete!")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()


def render_heatmap_results(results):
    """Render heatmap analysis results"""
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Statistics
    stats = results['statistics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Points Analyzed", stats['total_points'])
    
    with col2:
        st.metric("Average Score", f"{stats['avg_score']:.1f}/10")
    
    with col3:
        st.metric("Best Score", f"{stats['max_score']:.1f}/10")
    
    with col4:
        excellent_pct = (stats['excellent_count'] / stats['total_points']) * 100
        st.metric("Excellent Areas", f"{excellent_pct:.0f}%")
    
    # Heatmap
    st.markdown("### 🗺️ Suitability Heatmap")
    
    render_interactive_heatmap(results)
    
    st.markdown("---")
    
    # Best locations
    st.markdown("### 🎯 Top 5 Best Locations")
    
    best_locs = results['best_locations']
    
    for i, loc in enumerate(best_locs, 1):
        score = loc['suitability_score']
        
        # Color based on score
        if score >= 8:
            color = "🟢"
        elif score >= 6:
            color = "🟡"
        else:
            color = "🟠"
        
        with st.expander(f"{color} Location #{i} - Score: {score:.1f}/10", expanded=(i<=2)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Coordinates:**
                - Latitude: {loc['lat']:.6f}
                - Longitude: {loc['lon']:.6f}
                
                **Category:** {loc['category'].title()}
                """)
            
            with col2:
                st.markdown("**Why this location is good:**")
                for reason in loc['reasons']:
                    st.markdown(f"- {reason}")
    
    # Distribution chart
    st.markdown("### 📊 Suitability Distribution")
    
    render_distribution_chart(results)
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    for rec in results['recommendations']:
        st.info(rec)


def render_interactive_heatmap(results):
    """Render interactive heatmap with Folium"""
    
    # Get boundary for map center
    grid_points = results['grid_points']
    
    if not grid_points:
        st.error("No grid points to display")
        return
    
    # Calculate center
    lats = [p['lat'] for p in grid_points]
    lons = [p['lon'] for p in grid_points]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles='OpenStreetMap'
    )
    
    # Add satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False
    ).add_to(m)
    
    # Add heatmap
    heat_data = results['heatmap_data']
    
    HeatMap(
        heat_data,
        min_opacity=0.3,
        max_opacity=0.8,
        radius=25,
        blur=20,
        gradient={
            0.0: 'red',
            0.4: 'orange',
            0.6: 'yellow',
            0.8: 'lightgreen',
            1.0: 'green'
        }
    ).add_to(m)
    
    # Add markers for top 5 locations
    best_locs = results['best_locations'][:5]
    
    for i, loc in enumerate(best_locs, 1):
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            popup=folium.Popup(f"""
                <div style='width: 200px'>
                    <h4>Top Location #{i}</h4>
                    <b>Score:</b> {loc['suitability_score']:.1f}/10<br>
                    <b>Category:</b> {loc['category'].title()}<br>
                    <hr>
                    <b>Reasons:</b><br>
                    {'<br>'.join(['• ' + r for r in loc['reasons'][:3]])}
                </div>
            """, max_width=300),
            icon=folium.Icon(color='green' if i == 1 else 'blue', icon='star'),
            tooltip=f"#{i} - Score: {loc['suitability_score']:.1f}/10"
        ).add_to(m)
    
    # Layer control
    folium.LayerControl().add_to(m)
    
    # Display
    st_folium(m, width=800, height=500)
    
    # Legend
    st.markdown("""
    **Heatmap Colors:**
    - 🟢 **Green**: Excellent suitability (8-10)
    - 🟡 **Yellow**: Good suitability (6-8)
    - 🟠 **Orange**: Moderate suitability (4-6)
    - 🔴 **Red**: Poor suitability (0-4)
    
    ⭐ **Stars**: Top 5 best locations
    """)


def render_distribution_chart(results):
    """Render distribution chart of suitability scores"""
    
    grid_points = results['grid_points']
    
    # Create DataFrame
    df = pd.DataFrame([
        {
            'Score': p['suitability_score'],
            'Category': p['category'].title()
        }
        for p in grid_points
    ])
    
    # Histogram
    fig = px.histogram(
        df,
        x='Score',
        nbins=20,
        color='Category',
        title='Distribution of Suitability Scores',
        labels={'Score': 'Suitability Score (0-10)', 'count': 'Number of Points'},
        color_discrete_map={
            'Excellent': '#00ff00',
            'Good': '#90ee90',
            'Moderate': '#ffff00',
            'Poor': '#ff8c00'
        }
    )
    
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)
