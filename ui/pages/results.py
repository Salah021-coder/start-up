# ============================================================================
# FILE: ui/pages/results.py (FIXED - Proper Map Centering)
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd


def render():
    """Render enhanced results page with suitability map"""
    
    if not st.session_state.get('analysis_results'):
        st.warning("No analysis results available. Please run an analysis first.")
        if st.button("Start New Analysis"):
            st.session_state.current_page = 'analysis'
            st.rerun()
        return
    
    results = st.session_state.analysis_results
    
    # Header
    st.title("📊 Enhanced Analysis Results")
    st.markdown(f"**Analysis ID:** {results.get('analysis_id')}")
    
    # Data quality indicator
    data_sources = results.get('data_sources', {})
    infra_quality = data_sources.get('infrastructure', 'unknown')
    
    if infra_quality == 'real_osm':
        st.success("✅ Analysis uses real OpenStreetMap data for infrastructure")
    else:
        st.info("ℹ️ Analysis uses estimated data for infrastructure")
    
    # Summary metrics
    render_summary_metrics(results)
    
    st.markdown("---")
    
    # Location and accessibility summary
    render_location_summary(results)
    
    st.markdown("---")
    
    # ENHANCED: Suitability map with 5 classes
    render_suitability_map(results)
    
    st.markdown("---")
    
    # Recommendations
    render_recommendations(results)
    
    st.markdown("---")
    
    # Enhanced insights
    render_enhanced_insights(results)
    
    st.markdown("---")
    
    # Detailed criteria breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        render_criteria_scores(results)
    
    with col2:
        render_infrastructure_details(results)
    
    st.markdown("---")
    
    # Export options
    render_export_options(results)


def render_summary_metrics(results):
    """Render summary metrics"""
    st.markdown("### 📈 Summary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = results.get('overall_score', 0)
        delta = f"+{(score-5):.1f}" if score > 5 else f"{(score-5):.1f}"
        st.metric("Overall Score", f"{score:.1f}/10", delta=delta)
    
    with col2:
        confidence = results.get('confidence_level', 0) * 100
        st.metric("Confidence", f"{confidence:.0f}%")
    
    with col3:
        risk = results.get('risk_assessment', {}).get('level', 'medium')
        st.metric("Risk Level", risk.title())
    
    with col4:
        area = results.get('boundary', {}).get('area_hectares', 0)
        st.metric("Area", f"{area:.2f} ha")


def render_location_summary(results):
    """Render location and accessibility summary"""
    st.markdown("### 📍 Location Analysis")
    
    insights = results.get('key_insights', {})
    features = results.get('features', {})
    infra = features.get('infrastructure', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Location**")
        city = infra.get('city_name', 'Unknown')
        urban_level = infra.get('urbanization_level', 'unknown')
        st.info(f"📍 {city}\n\n🏘️ {urban_level.title()} area")
    
    with col2:
        st.markdown("**Accessibility**")
        access_score = infra.get('accessibility_score', 0)
        road_dist = infra.get('nearest_road_distance', 0)
        st.info(f"🚗 Score: {access_score:.1f}/10\n\n🛣️ Road: {road_dist:.0f}m")
    
    with col3:
        st.markdown("**Development**")
        dev_pressure = infra.get('development_pressure', 'unknown')
        pop_density = infra.get('population_density', 0)
        st.info(f"📊 {dev_pressure.title()} pressure\n\n👥 {pop_density:.0f} people/km²")
    
    # Full summaries
    st.markdown("**Quick Summary:**")
    st.write(insights.get('development_potential', 'Analysis complete'))


def render_suitability_map(results):
    """Render interactive suitability map with 5-class classification"""
    st.markdown("### 🗺️ Land Suitability Map")
    
    st.markdown("""
    This map shows the overall suitability classification of your land based on comprehensive analysis.
    The classification uses a weighted overlay of all factors to determine the best use potential.
    """)
    
    # Get data
    boundary = results.get('boundary', {})
    geojson = boundary.get('geojson', {})
    overall_score = results.get('overall_score', 5.0)
    
    # CRITICAL FIX: Extract centroid properly
    centroid = boundary.get('centroid')
    
    # If centroid is a list [lon, lat], we need [lat, lon] for Folium
    if centroid and isinstance(centroid, list) and len(centroid) == 2:
        # Check if it's [lon, lat] format (likely from GeoJSON)
        if -180 <= centroid[0] <= 180 and -90 <= centroid[1] <= 90:
            # If first value is in lon range and second in lat range
            if abs(centroid[0]) > abs(centroid[1]):
                # Likely [lon, lat], need to swap
                map_center = [centroid[1], centroid[0]]
            else:
                # Already [lat, lon]
                map_center = centroid
        else:
            map_center = [36.19, 5.41]  # Default fallback
    else:
        # Try to extract from geometry
        try:
            if geojson and 'geometry' in geojson:
                coords = geojson['geometry']['coordinates'][0]
                # Calculate centroid from coordinates
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                map_center = [sum(lats)/len(lats), sum(lons)/len(lons)]
            else:
                map_center = [36.19, 5.41]  # Default
        except:
            map_center = [36.19, 5.41]  # Default fallback
    
    # Debug: Show what we're using
    st.info(f"🗺️ Map centering on: Latitude {map_center[0]:.4f}, Longitude {map_center[1]:.4f}")
    
    # Determine suitability class
    suitability_class = classify_suitability(overall_score)
    
    # Create map with FIXED center
    m = folium.Map(
        location=map_center,
        zoom_start=16,  # Closer zoom
        tiles='OpenStreetMap'
    )
    
    # Add satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False
    ).add_to(m)
    
    # Add terrain layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Terrain',
        overlay=False
    ).add_to(m)
    
    # Get color based on suitability
    color_map = {
        'Very High': '#006400',  # Dark green
        'High': '#32CD32',       # Lime green
        'Moderate': '#FFD700',   # Gold
        'Low': '#FF8C00',        # Dark orange
        'Very Low': '#DC143C'    # Crimson
    }
    
    fill_color = color_map.get(suitability_class['class'], '#FFD700')
    
    # Add boundary with suitability color
    if geojson:
        # CRITICAL FIX: Make sure we're using the geometry correctly
        try:
            folium.GeoJson(
                geojson,
                style_function=lambda x: {
                    'fillColor': fill_color,
                    'color': fill_color,
                    'weight': 3,
                    'fillOpacity': 0.5
                },
                tooltip=folium.Tooltip(
                    f"""
                    <b>Land Suitability Analysis</b><br>
                    Class: {suitability_class['class']}<br>
                    Score: {overall_score:.1f}/10<br>
                    Rating: {suitability_class['rating']}
                    """,
                    sticky=True
                )
            ).add_to(m)
            
            # FIT BOUNDS TO GEOMETRY
            # Extract bounds from geometry
            if 'geometry' in geojson and 'coordinates' in geojson['geometry']:
                coords = geojson['geometry']['coordinates'][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                
                # Set bounds to fit the geometry
                bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]
                m.fit_bounds(bounds, padding=[50, 50])
                
        except Exception as e:
            st.error(f"Error adding boundary to map: {e}")
            # Add a marker at least
            folium.Marker(
                location=map_center,
                popup=f"Analysis Location<br>Score: {overall_score:.1f}/10",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
    
    # Add center marker with info
    folium.Marker(
        location=map_center,
        popup=folium.Popup(
            f"""
            <div style='width: 250px; font-family: Arial;'>
                <h3 style='color: {fill_color}; margin: 0;'>
                    {suitability_class['class']} Suitability
                </h3>
                <hr style='margin: 5px 0;'>
                <p style='margin: 5px 0;'>
                    <b>Overall Score:</b> {overall_score:.1f}/10<br>
                    <b>Rating:</b> {suitability_class['rating']}<br>
                    <b>Area:</b> {boundary.get('area_hectares', 0):.2f} ha
                </p>
                <hr style='margin: 5px 0;'>
                <p style='margin: 5px 0; font-size: 11px;'>
                    {suitability_class['description']}
                </p>
            </div>
            """,
            max_width=300
        ),
        icon=folium.Icon(
            color='green' if overall_score >= 7 else 'orange' if overall_score >= 5 else 'red',
            icon='star',
            prefix='fa'
        ),
        tooltip=f"Suitability: {suitability_class['class']}"
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Display map
    st_folium(m, width=800, height=500)
    
    # Display suitability classification
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background-color: {fill_color}; 
                    border-radius: 10px; color: white; margin: 10px 0;'>
            <h2 style='margin: 0; color: white;'>{suitability_class['class']} Suitability</h2>
            <p style='margin: 5px 0; font-size: 18px;'>{suitability_class['rating']}</p>
            <p style='margin: 5px 0; font-size: 14px;'>{suitability_class['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Suitability legend
    st.markdown("### 📊 Suitability Classification Legend")
    
    legend_data = {
        'Class': ['Very High', 'High', 'Moderate', 'Low', 'Very Low'],
        'Score Range': ['8.1 - 10.0', '6.1 - 8.0', '4.1 - 6.0', '2.1 - 4.0', '0.0 - 2.0'],
        'Color': ['🟢', '🟢', '🟡', '🟠', '🔴'],
        'Interpretation': [
            'Excellent conditions - Highly recommended',
            'Good conditions - Recommended with minor considerations',
            'Fair conditions - Suitable with some limitations',
            'Poor conditions - Major limitations present',
            'Very poor conditions - Not recommended'
        ]
    }
    
    df = pd.DataFrame(legend_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def classify_suitability(score: float) -> dict:
    """Classify suitability based on score (5-class system)"""
    
    if score > 8.0:
        return {
            'class': 'Very High',
            'rating': '⭐⭐⭐⭐⭐',
            'description': 'Excellent land with minimal constraints. Highly suitable for development.',
            'recommendation': 'Proceed with confidence'
        }
    elif score > 6.0:
        return {
            'class': 'High',
            'rating': '⭐⭐⭐⭐',
            'description': 'Good land with minor limitations. Suitable for most development types.',
            'recommendation': 'Recommended with standard precautions'
        }
    elif score > 4.0:
        return {
            'class': 'Moderate',
            'rating': '⭐⭐⭐',
            'description': 'Fair land with some constraints. Suitable with careful planning.',
            'recommendation': 'Feasible with additional considerations'
        }
    elif score > 2.0:
        return {
            'class': 'Low',
            'rating': '⭐⭐',
            'description': 'Poor land with significant limitations. Development will be challenging.',
            'recommendation': 'Requires major mitigation measures'
        }
    else:
        return {
            'class': 'Very Low',
            'rating': '⭐',
            'description': 'Very poor land with severe constraints. Not recommended for development.',
            'recommendation': 'Consider alternative locations'
        }


def render_infrastructure_details(results):
    """Render detailed infrastructure breakdown"""
    st.markdown("### 🏗️ Infrastructure Details")
    
    features = results.get('features', {})
    infra = features.get('infrastructure', {})
    
    # Transportation
    with st.expander("🚗 Transportation", expanded=True):
        st.markdown(f"""
        - **Nearest Road:** {infra.get('nearest_road_distance', 0):.0f}m ({infra.get('road_type', 'unknown')})
        - **Primary Road:** {infra.get('primary_road_distance', 0)/1000:.1f}km
        - **Motorway:** {infra.get('motorway_distance', 0)/1000:.1f}km
        - **Road Density:** {infra.get('road_density', 0):.1f} km/km²
        """)
    
    # Public Transport
    with st.expander("🚌 Public Transport"):
        st.markdown(f"""
        - **Bus Stop:** {infra.get('bus_stop_distance', 0):.0f}m
        - **Train Station:** {infra.get('train_station_distance', 0)/1000:.1f}km
        - **Transport Score:** {infra.get('public_transport_score', 0):.1f}/10
        """)
    
    # Amenities
    with st.expander("🏪 Amenities"):
        st.markdown(f"""
        **Education:**
        - Schools (3km): {infra.get('schools_count_3km', 0)}
        
        **Healthcare:**
        - Hospitals (5km): {infra.get('hospitals_count_5km', 0)}
        - Clinics (2km): {infra.get('clinics_count_2km', 0)}
        
        **Shopping:**
        - Supermarkets (2km): {infra.get('supermarkets_count_2km', 0)}
        - Restaurants (1km): {infra.get('restaurants_count_1km', 0)}
        
        **Total Amenities:** {infra.get('total_amenities', 0)}
        """)
    
    # Utilities
    with st.expander("⚡ Utilities"):
        utilities = {
            'Electricity': infra.get('electricity_grid', False),
            'Water': infra.get('water_network', False),
            'Sewage': infra.get('sewage_system', False),
            'Gas': infra.get('gas_network', False),
            'Internet': infra.get('internet_fiber', False)
        }
        
        for utility, available in utilities.items():
            status = "✅" if available else "❌"
            st.markdown(f"- {status} {utility}")


def render_enhanced_insights(results):
    """Render comprehensive insights"""
    st.markdown("### 💡 Detailed Insights")
    
    insights = results.get('key_insights', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Strengths
        strengths = insights.get('strengths', [])
        if strengths:
            st.markdown("**✅ Key Strengths:**")
            for strength in strengths:
                st.success(strength)
        
        # Opportunities
        opportunities = insights.get('opportunities', [])
        if opportunities:
            st.markdown("**💡 Opportunities:**")
            for opp in opportunities:
                st.info(opp)
    
    with col2:
        # Concerns
        concerns = insights.get('concerns', [])
        if concerns:
            st.markdown("**⚠️ Considerations:**")
            for concern in concerns:
                st.warning(concern)


def render_recommendations(results):
    """Render recommendations section"""
    st.markdown("### 🎯 Usage Recommendations")
    
    recommendations = results.get('recommendations', [])
    
    for rec in recommendations[:3]:
        rank = rec.get('rank', 0)
        usage = rec.get('usage_type', 'Unknown')
        score = rec.get('suitability_score', 0)
        factors = rec.get('supporting_factors', [])
        
        with st.expander(f"#{rank} - {usage.title()} (Score: {score:.1f}/10)", expanded=(rank==1)):
            st.markdown("**Supporting Factors:**")
            for factor in factors:
                st.markdown(f"- ✅ {factor}")
            
            concerns = rec.get('concerns', [])
            if concerns:
                st.markdown("**Concerns:**")
                for concern in concerns:
                    st.markdown(f"- ⚠️ {concern}")
            
            # Visual score bar
            st.progress(score / 10)


def render_criteria_scores(results):
    """Render criteria scores visualization"""
    st.markdown("### 📈 Criteria Evaluation")
    
    features = results.get('features', {})
    terrain = features.get('terrain', {})
    env = features.get('environmental', {})
    infra = features.get('infrastructure', {})
    
    criteria = [
        'Terrain Suitability',
        'Infrastructure Access',
        'Environmental Factors',
        'Vegetation Health',
        'Water Resources',
        'Risk Assessment'
    ]
    
    scores = [
        terrain.get('buildability_score', 5) * 10,
        infra.get('accessibility_score', 5) * 10,
        env.get('environmental_score', 5) * 10,
        env.get('ndvi_avg', 0.5) * 100,
        (1 - env.get('flood_risk_percent', 0) / 100) * 100,
        100 - (results.get('risk_assessment', {}).get('risk_count', 0) * 20)
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            x=scores, 
            y=criteria, 
            orientation='h',
            marker_color=['#00ff00' if s >= 70 else '#ffff00' if s >= 40 else '#ff8c00' for s in scores],
            text=[f"{s:.0f}%" for s in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Criteria Scores (%)",
        xaxis_title="Score",
        height=400,
        showlegend=False,
        xaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_export_options(results):
    """Render export options"""
    st.markdown("### 📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download PDF Report", use_container_width=True):
            st.info("PDF generation feature coming soon!")
    
    with col2:
        if st.button("📊 Export Data (CSV)", use_container_width=True):
            import pandas as pd
            
            # Create simple CSV export
            data = {
                'Metric': ['Overall Score', 'Confidence', 'Risk Level', 'Area (ha)'],
                'Value': [
                    results.get('overall_score', 0),
                    results.get('confidence_level', 0),
                    results.get('risk_assessment', {}).get('level', 'N/A'),
                    results.get('boundary', {}).get('area_hectares', 0)
                ]
            }
            df = pd.DataFrame(data)
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="land_analysis.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🗺️ Export Map (GeoJSON)", use_container_width=True):
            import json
            
            geojson = results.get('boundary', {}).get('geojson', {})
            geojson_str = json.dumps(geojson, indent=2)
            
            st.download_button(
                label="Download GeoJSON",
                data=geojson_str,
                file_name="boundary.geojson",
                mime="application/json"
            )
