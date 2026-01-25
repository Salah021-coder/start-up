# ============================================================================
# FILE: ui/pages/results.py (COMPLETE WITH ANALYSIS MAP)
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import numpy as np

def render():
    """Render results page with analysis visualization map"""
    
    if not st.session_state.get('analysis_results'):
        st.warning("No analysis results available. Please run an analysis first.")
        if st.button("Start New Analysis"):
            st.session_state.current_page = 'analysis'
            st.rerun()
        return
    
    results = st.session_state.analysis_results
    
    # Header
    st.title("📊 Analysis Results")
    st.markdown(f"**Analysis ID:** {results.get('analysis_id')}")
    
    # Summary metrics
    st.markdown("### Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = results.get('overall_score', 0)
        st.metric("Overall Score", f"{score:.1f}/10", 
                 delta=f"{(score-5):.1f}" if score > 5 else None)
    
    with col2:
        confidence = results.get('confidence_level', 0) * 100
        st.metric("Confidence", f"{confidence:.0f}%")
    
    with col3:
        risk = results.get('risk_assessment', {}).get('level', 'medium')
        st.metric("Risk Level", risk.title())
    
    with col4:
        area = results.get('boundary', {}).get('area_hectares', 0)
        st.metric("Area", f"{area:.2f} ha")
    
    st.markdown("---")
    
    # ==========================================
    # ANALYSIS MAP - MAIN VISUALIZATION
    # ==========================================
    render_analysis_map(results)
    
    st.markdown("---")
    
    # Recommendations
    render_recommendations(results)
    
    st.markdown("---")
    
    # Detailed scores
    col1, col2 = st.columns(2)
    
    with col1:
        render_criteria_scores(results)
    
    with col2:
        render_insights(results)
    
    st.markdown("---")
    
    # Export options
    render_export_options(results)


def render_analysis_map(results):
    """
    Render the main analysis visualization map
    Shows the analyzed land with color-coded suitability
    """
    st.markdown("### 🗺️ Land Analysis Visualization")
    
    boundary_data = results.get('boundary', {})
    features = results.get('features', {})
    overall_score = results.get('overall_score', 5)
    
    # Create map centered on the analyzed area
    centroid = boundary_data.get('centroid', [5.41, 36.19])
    
    m = folium.Map(
        location=[centroid[1], centroid[0]],  # [lat, lon]
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # Add satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Determine color based on suitability score
    def get_suitability_color(score):
        """Get color based on suitability score"""
        if score >= 8:
            return '#00ff00'  # Green - Excellent
        elif score >= 6:
            return '#90ee90'  # Light Green - Good
        elif score >= 4:
            return '#ffff00'  # Yellow - Moderate
        elif score >= 2:
            return '#ff8c00'  # Orange - Poor
        else:
            return '#ff0000'  # Red - Unsuitable
    
    color = get_suitability_color(overall_score)
    
    # Add the analyzed boundary with color coding
    folium.GeoJson(
        boundary_data.get('geojson'),
        name='Analyzed Area',
        style_function=lambda x: {
            'fillColor': color,
            'color': '#000000',
            'weight': 3,
            'fillOpacity': 0.4,
            'opacity': 1
        },
        tooltip=f"Score: {overall_score:.1f}/10"
    ).add_to(m)
    
    # Add markers for key features
    add_feature_markers(m, centroid, features, results)
    
    # Add legend
    add_suitability_legend(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Display the map
    st_folium(m, width=800, height=500, returned_objects=[])
    
    # Map interpretation
    st.markdown("**Map Legend:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Green**: Excellent (8-10)")
        st.markdown("🟡 **Yellow**: Moderate (4-6)")
    with col2:
        st.markdown("🟢 **Light Green**: Good (6-8)")
        st.markdown("🟠 **Orange**: Poor (2-4)")
    with col3:
        st.markdown("🔴 **Red**: Unsuitable (0-2)")


def add_feature_markers(m, centroid, features, results):
    """Add markers showing key features and insights"""
    
    terrain = features.get('terrain', {})
    env = features.get('environmental', {})
    infra = features.get('infrastructure', {})
    
    # Center marker with summary
    folium.Marker(
        location=[centroid[1], centroid[0]],
        popup=folium.Popup(f"""
            <div style='width: 200px'>
                <h4>Analysis Summary</h4>
                <b>Overall Score:</b> {results.get('overall_score', 0):.1f}/10<br>
                <b>Top Use:</b> {results.get('recommendations', [{}])[0].get('usage_type', 'N/A')}<br>
                <b>Confidence:</b> {results.get('confidence_level', 0)*100:.0f}%
            </div>
        """, max_width=300),
        icon=folium.Icon(color='blue', icon='info-sign'),
        tooltip="Click for summary"
    ).add_to(m)
    
    # Terrain info marker
    if terrain:
        offset_lat = centroid[1] + 0.002
        folium.Marker(
            location=[offset_lat, centroid[0]],
            popup=f"""
                <b>Terrain Features:</b><br>
                Slope: {terrain.get('slope_avg', 0):.1f}°<br>
                Elevation: {terrain.get('elevation_avg', 0):.0f}m<br>
                Buildability: {terrain.get('buildability_score', 0):.1f}/10
            """,
            icon=folium.Icon(color='green', icon='triangle-top', prefix='fa'),
            tooltip="Terrain Data"
        ).add_to(m)
    
    # Environmental marker
    if env:
        offset_lon = centroid[0] + 0.002
        folium.Marker(
            location=[centroid[1], offset_lon],
            popup=f"""
                <b>Environmental:</b><br>
                NDVI: {env.get('ndvi_avg', 0):.2f}<br>
                Flood Risk: {env.get('flood_risk_level', 'N/A')}<br>
                Env Score: {env.get('environmental_score', 0):.1f}/10
            """,
            icon=folium.Icon(color='lightgreen', icon='leaf'),
            tooltip="Environment Data"
        ).add_to(m)
    
    # Risk marker (if high risk)
    if results.get('risk_assessment', {}).get('level') == 'high':
        offset_lat = centroid[1] - 0.002
        folium.Marker(
            location=[offset_lat, centroid[0]],
            popup=f"""
                <b>⚠️ Risk Factors:</b><br>
                Level: High<br>
                See insights for details
            """,
            icon=folium.Icon(color='red', icon='warning', prefix='fa'),
            tooltip="Risk Warning"
        ).add_to(m)


def add_suitability_legend(m):
    """Add a color legend to the map"""
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px; height: 180px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
        <p style="margin-bottom: 5px;"><b>Suitability Scale</b></p>
        <p style="margin: 3px;"><span style="background-color: #00ff00; padding: 3px 10px;">■</span> Excellent (8-10)</p>
        <p style="margin: 3px;"><span style="background-color: #90ee90; padding: 3px 10px;">■</span> Good (6-8)</p>
        <p style="margin: 3px;"><span style="background-color: #ffff00; padding: 3px 10px;">■</span> Moderate (4-6)</p>
        <p style="margin: 3px;"><span style="background-color: #ff8c00; padding: 3px 10px;">■</span> Poor (2-4)</p>
        <p style="margin: 3px;"><span style="background-color: #ff0000; padding: 3px 10px;">■</span> Unsuitable (0-2)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))


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


def render_insights(results):
    """Render key insights"""
    st.markdown("### 💡 Key Insights")
    
    insights = results.get('key_insights', {})
    
    strengths = insights.get('strengths', [])
    if strengths:
        st.markdown("**Strengths:**")
        for strength in strengths:
            st.success(f"✅ {strength}")
    
    concerns = insights.get('concerns', [])
    if concerns:
        st.markdown("**Concerns:**")
        for concern in concerns:
            st.warning(f"⚠️ {concern}")
    
    opportunities = insights.get('opportunities', [])
    if opportunities:
        st.markdown("**Opportunities:**")
        for opp in opportunities:
            st.info(f"💡 {opp}")


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