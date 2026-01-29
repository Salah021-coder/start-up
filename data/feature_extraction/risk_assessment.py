# ============================================================================
# FILE: ui/pages/risk_analysis.py
# Dedicated Risk Assessment Page
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import folium
from streamlit_folium import st_folium
from typing import Dict, List
import numpy as np


def render():
    """Render dedicated risk assessment page"""
    
    st.title("🛡️ Comprehensive Risk Assessment")
    
    # Check if analysis results exist
    if not st.session_state.get('analysis_results'):
        st.warning("⚠️ No analysis results available. Please run an analysis first.")
        if st.button("Start New Analysis"):
            st.session_state.current_page = 'analysis'
            st.rerun()
        return
    
    results = st.session_state.analysis_results
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    if not comprehensive_risks:
        st.warning("""
        ⚠️ **Comprehensive Risk Assessment Not Available**
        
        This analysis was performed without Google Earth Engine access.
        Only basic risk assessment is available.
        
        To access comprehensive risk assessment (7 risk types):
        - Configure Google Earth Engine credentials
        - Re-run the analysis
        """)
        return
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🔍 Detailed Risks", 
        "🗺️ Risk Map",
        "🛠️ Mitigation",
        "📈 Comparison"
    ])
    
    with tab1:
        render_risk_overview(comprehensive_risks, results)
    
    with tab2:
        render_detailed_risks(comprehensive_risks)
    
    with tab3:
        render_risk_map(comprehensive_risks, results)
    
    with tab4:
        render_mitigation_strategies(comprehensive_risks)
    
    with tab5:
        render_risk_comparison(comprehensive_risks)


# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

def render_risk_overview(risks: Dict, results: Dict):
    """Render risk overview dashboard"""
    
    st.markdown("## 📊 Risk Profile Summary")
    
    overall = risks.get('overall', {})
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        level = overall.get('level', 'unknown')
        color = get_risk_color(level)
        st.markdown(f"""
        <div style='background-color:{color};padding:25px;border-radius:12px;text-align:center;'>
            <h2 style='color:white;margin:0;font-size:28px;'>{level.replace('_', ' ').title()}</h2>
            <p style='color:white;margin:8px 0 0 0;font-size:14px;'>Overall Risk Level</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_severity = overall.get('average_severity', 0)
        st.metric(
            "Average Severity",
            f"{avg_severity:.1f}/5",
            help="Average across all 7 risk types"
        )
        st.progress(avg_severity / 5)
    
    with col3:
        high_count = overall.get('high_risk_count', 0)
        st.metric(
            "Critical Risks",
            high_count,
            delta="Requires Immediate Attention" if high_count > 0 else "None",
            delta_color="inverse"
        )
    
    with col4:
        medium_count = overall.get('medium_risk_count', 0)
        st.metric(
            "Moderate Risks",
            medium_count,
            delta="Planning Required" if medium_count > 0 else "None",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Summary text
    summary = risks.get('summary', [])
    if summary:
        st.markdown("### 📋 Executive Summary")
        for line in summary:
            st.markdown(line)
    
    st.markdown("---")
    
    # Risk matrix visualization
    st.markdown("### 🎯 Risk Matrix")
    render_risk_matrix(risks)
    
    st.markdown("---")
    
    # Quick risk cards
    st.markdown("### 🔍 Risk Type Overview")
    
    risk_types = [
        ('flood', '🌊', 'Flood'),
        ('landslide', '⛰️', 'Landslide'),
        ('erosion', '🌾', 'Erosion'),
        ('seismic', '🏗️', 'Seismic'),
        ('drought', '💧', 'Drought'),
        ('wildfire', '🔥', 'Wildfire'),
        ('subsidence', '🏚️', 'Subsidence')
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for idx, (risk_key, emoji, name) in enumerate(risk_types):
        risk_data = risks.get(risk_key, {})
        if risk_data:
            with cols[idx % 4]:
                render_risk_quick_card(emoji, name, risk_data)
    
    st.markdown("---")
    
    # Development impact assessment
    st.markdown("### 💰 Development Impact Assessment")
    render_development_impact(risks, results)


def render_risk_matrix(risks: Dict):
    """Render risk probability vs impact matrix"""
    
    risk_types = {
        'flood': '🌊 Flood',
        'landslide': '⛰️ Landslide',
        'erosion': '🌾 Erosion',
        'seismic': '🏗️ Seismic',
        'drought': '💧 Drought',
        'wildfire': '🔥 Wildfire',
        'subsidence': '🏚️ Subsidence'
    }
    
    # Create data for matrix
    matrix_data = []
    
    for risk_key, risk_name in risk_types.items():
        risk_data = risks.get(risk_key, {})
        if risk_data and risk_data.get('level') != 'unknown':
            severity = risk_data.get('severity', 0)
            score = risk_data.get('score', 0)
            
            # Probability (based on score)
            probability = score / 20  # 0-5 scale
            
            # Impact (severity)
            impact = severity
            
            matrix_data.append({
                'Risk Type': risk_name,
                'Probability': probability,
                'Impact': impact,
                'Severity': severity
            })
    
    if not matrix_data:
        st.info("No risk data available for matrix")
        return
    
    df = pd.DataFrame(matrix_data)
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='Probability',
        y='Impact',
        size='Severity',
        color='Severity',
        text='Risk Type',
        title='Risk Probability vs Impact Matrix',
        labels={
            'Probability': 'Probability (0-5)',
            'Impact': 'Impact (0-5)'
        },
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        size_max=40
    )
    
    # Add quadrant lines
    fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=2.5, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=1.25, y=4.5, text="Low Probability<br>High Impact", showarrow=False, opacity=0.3)
    fig.add_annotation(x=3.75, y=4.5, text="High Probability<br>High Impact", showarrow=False, opacity=0.3)
    fig.add_annotation(x=1.25, y=1.25, text="Low Probability<br>Low Impact", showarrow=False, opacity=0.3)
    fig.add_annotation(x=3.75, y=1.25, text="High Probability<br>Low Impact", showarrow=False, opacity=0.3)
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=500, xaxis_range=[0, 5], yaxis_range=[0, 5])
    
    st.plotly_chart(fig, use_container_width=True)


def render_risk_quick_card(emoji: str, name: str, risk_data: Dict):
    """Render quick risk card"""
    
    level = risk_data.get('level', 'unknown')
    severity = risk_data.get('severity', 0)
    color = get_severity_color(severity)
    
    st.markdown(f"""
    <div style='background-color:{color};padding:15px;border-radius:10px;text-align:center;margin-bottom:10px;'>
        <p style='font-size:30px;margin:0;'>{emoji}</p>
        <p style='font-weight:bold;margin:8px 0 5px 0;font-size:16px;'>{name}</p>
        <p style='margin:0;font-size:13px;'>{level.replace('_', ' ').title()}</p>
        <p style='margin:5px 0 0 0;font-size:20px;font-weight:bold;'>{severity}/5</p>
    </div>
    """, unsafe_allow_html=True)


def render_development_impact(risks: Dict, results: Dict):
    """Render development cost and timeline impact"""
    
    overall = risks.get('overall', {})
    high_count = overall.get('high_risk_count', 0)
    medium_count = overall.get('medium_risk_count', 0)
    
    # Calculate impact multipliers
    cost_multiplier = 1.0 + (high_count * 0.25) + (medium_count * 0.10)
    time_multiplier = 1.0 + (high_count * 0.20) + (medium_count * 0.08)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Cost Impact",
            f"+{(cost_multiplier - 1) * 100:.0f}%",
            delta="Above baseline",
            delta_color="inverse",
            help="Estimated increase in development costs due to risk mitigation"
        )
    
    with col2:
        st.metric(
            "Timeline Impact",
            f"+{(time_multiplier - 1) * 100:.0f}%",
            delta="Additional time",
            delta_color="inverse",
            help="Estimated increase in project timeline due to risk assessment and mitigation"
        )
    
    with col3:
        insurance_level = "High" if high_count >= 2 else "Moderate" if medium_count >= 2 else "Standard"
        st.metric(
            "Insurance Requirement",
            insurance_level,
            help="Recommended insurance coverage level"
        )
    
    # Detailed breakdown
    with st.expander("📊 View Detailed Cost Breakdown"):
        st.markdown(f"""
        **Base Development Cost:** 100%
        
        **Risk Mitigation Costs:**
        - High-severity risks: +{high_count * 25}% ({high_count} × 25%)
        - Medium-severity risks: +{medium_count * 10}% ({medium_count} × 10%)
        
        **Total Estimated Cost:** {cost_multiplier * 100:.0f}%
        
        **Additional Time Required:**
        - Risk assessments and studies: +{high_count * 10}%
        - Mitigation implementation: +{(high_count + medium_count) * 5}%
        - Regulatory approvals: +{high_count * 5}%
        
        **Total Timeline Extension:** {time_multiplier * 100:.0f}%
        
        *Note: These are rough estimates. Actual costs depend on specific mitigation strategies.*
        """)


# ============================================================================
# TAB 2: DETAILED RISKS
# ============================================================================

def render_detailed_risks(risks: Dict):
    """Render detailed risk analysis for each type"""
    
    st.markdown("## 🔍 Detailed Risk Analysis")
    
    risk_types = [
        ('flood', '🌊', 'Flood Risk'),
        ('landslide', '⛰️', 'Landslide Risk'),
        ('erosion', '🌾', 'Erosion Risk'),
        ('seismic', '🏗️', 'Seismic Risk'),
        ('drought', '💧', 'Drought Risk'),
        ('wildfire', '🔥', 'Wildfire Risk'),
        ('subsidence', '🏚️', 'Subsidence Risk')
    ]
    
    for risk_key, emoji, title in risk_types:
        risk_data = risks.get(risk_key, {})
        
        if not risk_data or risk_data.get('level') == 'unknown':
            continue
        
        severity = risk_data.get('severity', 0)
        level = risk_data.get('level', 'unknown')
        
        # Expand high-risk items by default
        expanded = severity >= 4
        
        with st.expander(f"{emoji} **{title}** - {level.replace('_', ' ').title()}", expanded=expanded):
            render_detailed_risk_card(risk_data, emoji, title, risk_key)
    
    st.markdown("---")
    
    # Severity comparison chart
    st.markdown("### 📊 Risk Severity Comparison")
    render_risk_severity_chart(risks, risk_types)


def render_detailed_risk_card(risk_data: Dict, emoji: str, title: str, risk_key: str):
    """Render detailed information for a specific risk"""
    
    severity = risk_data.get('severity', 0)
    score = risk_data.get('score', 0)
    level = risk_data.get('level', 'unknown')
    description = risk_data.get('description', 'No description available')
    factors = risk_data.get('primary_factors', [])
    impact = risk_data.get('impact', 'Impact unknown')
    
    # Header with severity and score
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        color = get_severity_color(severity)
        st.markdown(f"""
        <div style='background-color:{color};padding:20px;border-radius:10px;text-align:center;'>
            <h2 style='color:white;margin:0;font-size:36px;'>{severity}/5</h2>
            <p style='color:white;margin:8px 0 0 0;font-size:13px;'>Severity</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**Risk Level:** {level.replace('_', ' ').title()}")
        st.markdown(f"**Risk Score:** {score:.1f}/100")
        st.progress(min(score / 100, 1.0))
    
    with col3:
        # Risk-specific metrics
        render_risk_specific_metrics(risk_data, risk_key)
    
    st.markdown("---")
    
    # Description
    st.markdown(f"### 📝 Description")
    st.info(description)
    
    # Primary factors
    if factors:
        st.markdown("### 🔍 Key Contributing Factors")
        for factor in factors:
            st.markdown(f"• {factor}")
    
    # Impact
    st.markdown("### ⚠️ Potential Impact")
    st.warning(impact)
    
    # Risk-specific visualizations
    st.markdown("---")
    render_risk_specific_visualization(risk_data, risk_key)


def render_risk_specific_metrics(risk_data: Dict, risk_key: str):
    """Render risk-specific metrics"""
    
    if risk_key == 'flood':
        water_occ = risk_data.get('water_occurrence', 0)
        st.metric("Water Occurrence", f"{water_occ:.0f}%")
    
    elif risk_key == 'landslide':
        slope_max = risk_data.get('slope_max', 0)
        st.metric("Max Slope", f"{slope_max:.1f}°")
    
    elif risk_key == 'erosion':
        slope = risk_data.get('slope', 0)
        st.metric("Avg Slope", f"{slope:.1f}°")
    
    elif risk_key == 'seismic':
        zone = risk_data.get('seismic_zone', 'Unknown')
        st.metric("Seismic Zone", zone)
    
    elif risk_key == 'drought':
        veg_health = risk_data.get('vegetation_health', 0)
        st.metric("Vegetation Health", f"{veg_health:.2f}")
    
    elif risk_key == 'wildfire':
        veg_density = risk_data.get('vegetation_density', 0)
        st.metric("Vegetation Density", f"{veg_density:.2f}")
    
    elif risk_key == 'subsidence':
        elevation = risk_data.get('elevation', 0)
        st.metric("Elevation", f"{elevation:.0f}m")


def render_risk_specific_visualization(risk_data: Dict, risk_key: str):
    """Render risk-specific visualizations"""
    
    st.markdown("### 📈 Risk Analysis")
    
    if risk_key == 'flood':
        # Flood risk breakdown
        water_occ = risk_data.get('water_occurrence', 0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Water Occurrence', 'Drainage', 'Elevation'],
                y=[water_occ, max(0, 100 - water_occ), 50],
                marker_color=['#1e88e5', '#43a047', '#fb8c00']
            )
        ])
        fig.update_layout(
            title='Flood Risk Factors',
            yaxis_title='Contribution (%)',
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif risk_key == 'landslide':
        # Landslide risk factors
        slope_avg = risk_data.get('slope_avg', 0)
        slope_max = risk_data.get('slope_max', 0)
        
        fig = go.Figure(data=[
            go.Indicator(
                mode="gauge+number",
                value=slope_max,
                title={'text': "Maximum Slope (°)"},
                gauge={
                    'axis': {'range': [None, 50]},
                    'bar': {'color': "red"},
                    'steps': [
                        {'range': [0, 15], 'color': "lightgreen"},
                        {'range': [15, 30], 'color': "yellow"},
                        {'range': [30, 50], 'color': "orange"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': slope_max
                    }
                }
            )
        ])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    elif risk_key == 'seismic':
        # Seismic zone map (placeholder)
        zone = risk_data.get('seismic_zone', 'Unknown')
        lat = risk_data.get('latitude', 36.19)
        
        st.markdown(f"""
        **Seismic Zone:** {zone}
        
        **Building Code Requirements:**
        - Seismic-resistant design mandatory
        - Special foundation requirements
        - Reinforced concrete specifications
        - Regular structural inspections
        
        **Location:** Latitude {lat:.2f}°
        """)


def render_risk_severity_chart(risks: Dict, risk_types: list):
    """Render horizontal bar chart comparing all risk severities"""
    
    risk_names = []
    severities = []
    scores = []
    colors = []
    
    for risk_key, emoji, title in risk_types:
        risk_data = risks.get(risk_key, {})
        
        if risk_data and risk_data.get('level') != 'unknown':
            risk_names.append(f"{emoji} {title.replace(' Risk', '')}")
            severity = risk_data.get('severity', 0)
            severities.append(severity)
            scores.append(risk_data.get('score', 0))
            colors.append(get_severity_color(severity))
    
    if not severities:
        st.info("No risk data available for chart")
        return
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=risk_names,
            x=severities,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{s}/5 (Score: {scores[i]:.0f})" for i, s in enumerate(severities)],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Risk Severity Levels (0-5 scale)",
        xaxis_title="Severity Level",
        height=400,
        showlegend=False,
        xaxis=dict(range=[0, 5])
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# TAB 3: RISK MAP
# ============================================================================

def render_risk_map(risks: Dict, results: Dict):
    """Render risk visualization on map"""
    
    st.markdown("## 🗺️ Risk Visualization Map")
    
    boundary = results.get('boundary', {})
    centroid = boundary.get('centroid', [5.41, 36.19])
    geojson = boundary.get('geojson')
    
    # Create map
    m = folium.Map(
        location=[centroid[1], centroid[0]],
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # Add satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False
    ).add_to(m)
    
    # Add boundary
    if geojson:
        overall = risks.get('overall', {})
        level = overall.get('level', 'medium')
        color = get_risk_color(level)
        
        folium.GeoJson(
            geojson,
            style_function=lambda x: {
                'fillColor': color,
                'color': color,
                'weight': 3,
                'fillOpacity': 0.3
            },
            tooltip=f"Overall Risk: {level.replace('_', ' ').title()}"
        ).add_to(m)
    
    # Add risk markers
    risk_types = {
        'flood': ('🌊', 'blue'),
        'landslide': ('⛰️', 'orange'),
        'erosion': ('🌾', 'brown'),
        'seismic': ('🏗️', 'red'),
        'drought': ('💧', 'lightblue'),
        'wildfire': ('🔥', 'darkred'),
        'subsidence': ('🏚️', 'gray')
    }
    
    # Calculate positions for risk markers around centroid
    positions = [
        (0.002, 0.002),   # NE
        (0.002, -0.002),  # SE
        (-0.002, -0.002), # SW
        (-0.002, 0.002),  # NW
        (0.003, 0),       # E
        (0, 0.003),       # N
        (-0.003, 0)       # W
    ]
    
    for idx, (risk_key, (emoji, color)) in enumerate(risk_types.items()):
        risk_data = risks.get(risk_key, {})
        
        if risk_data and risk_data.get('level') != 'unknown':
            severity = risk_data.get('severity', 0)
            level = risk_data.get('level', 'unknown')
            description = risk_data.get('description', '')
            
            if idx < len(positions):
                pos = positions[idx]
                lat = centroid[1] + pos[1]
                lon = centroid[0] + pos[0]
                
                # Create popup content
                popup_html = f"""
                <div style='width: 200px'>
                    <h4>{emoji} {risk_key.title()} Risk</h4>
                    <b>Level:</b> {level.replace('_', ' ').title()}<br>
                    <b>Severity:</b> {severity}/5<br>
                    <hr>
                    <p style='font-size:12px'>{description}</p>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=color, icon='exclamation-triangle'),
                    tooltip=f"{emoji} {risk_key.title()}: {level.replace('_', ' ').title()}"
                ).add_to(m)
    
    # Add legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: auto; 
                background-color: white; z-index:9999; font-size:12px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
        <h4 style="margin:0 0 10px 0">Risk Levels</h4>
        <div style="background:#d32f2f;padding:3px;margin:2px;border-radius:3px;color:white">Very High</div>
        <div style="background:#f57c00;padding:3px;margin:2px;border-radius:3px;color:white">High</div>
        <div style="background:#fbc02d;padding:3px;margin:2px;border-radius:3px">Medium</div>
        <div style="background:#388e3c;padding:3px;margin:2px;border-radius:3px;color:white">Low</div>
        <div style="background:#1b5e20;padding:3px;margin:2px;border-radius:3px;color:white">Very Low</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Layer control
    folium.LayerControl().add_to(m)
    
    # Display map
    st_folium(m, width=800, height=600)
    
    st.markdown("""
    **Map Legend:**
    - **Boundary Color**: Overall risk level
    - **Markers**: Individual risk types
    - Click on markers for detailed risk information
    """)


# ============================================================================
# TAB 4: MITIGATION STRATEGIES
# ============================================================================

def render_mitigation_strategies(risks: Dict):
    """Render mitigation strategies and recommendations"""
    
    st.markdown("## 🛠️ Risk Mitigation Strategies")
    
    # Overall recommendations
    mitigation = risks.get('mitigation', [])
    
    if mitigation:
        st.markdown("### 🎯 Priority Actions")
        for idx, recommendation in enumerate(mitigation, 1):
            st.info(f"**{idx}.** {recommendation}")
    
    st.markdown("---")
    
    # Detailed mitigation by risk type
    st.markdown("### 📋 Detailed Mitigation Plans")
    
    risk_types = [
        ('flood', '🌊', 'Flood Risk'),
        ('landslide', '⛰️', 'Landslide Risk'),
        ('erosion', '🌾', 'Erosion Risk'),
        ('seismic', '🏗️', 'Seismic Risk'),
        ('drought', '💧', 'Drought Risk'),
        ('wildfire', '🔥', 'Wildfire Risk'),
        ('subsidence', '🏚️', 'Subsidence Risk')
    ]
    
    for risk_key, emoji, title in risk_types:
        risk_data = risks.get(risk_key, {})
        
        if not risk_data or risk_data.get('level') == 'unknown':
            continue
        
        severity = risk_data.get('severity', 0)
        
        # Only show mitigation for medium+ risks
        if severity >= 3:
            with st.expander(f"{emoji} {title} Mitigation Plan"):
                render_mitigation_plan(risk_key, risk_data)
    
    st.markdown("---")
    
    # Cost estimation
    st.markdown("### 💰 Mitigation Cost Estimation")
    render_mitigation_costs(risks)
    
    st.markdown("---")
    
    # Timeline
    st.markdown("### 📅 Implementation Timeline")
    render_mitigation_timeline(risks)


def render_mitigation_plan(risk_key: str, risk_data: Dict):
    """Render detailed mitigation plan for specific risk"""
    
    severity = risk_data.get('severity', 0)
    
    mitigation_plans = {
        'flood': {
            'immediate': [
                "Conduct detailed flood risk survey",
                "Install temporary drainage systems",
                "Elevate critical infrastructure"
            ],
            'short_term': [
                "Install comprehensive drainage network",
                "Build retention basins",
                "Implement erosion control measures",
                "Purchase flood insurance"
            ],
            'long_term': [
                "Construct permanent flood barriers",
                "Implement sustainable urban drainage systems (SUDS)",
                "Develop emergency evacuation plans",
                "Regular maintenance of drainage systems"
            ],
            'cost_range': "$50,000 - $500,000"
        },
        'landslide': {
            'immediate': [
                "Geotechnical investigation",
                "Identify unstable slopes",
                "Install warning systems"
            ],
            'short_term': [
                "Build retaining walls on critical slopes",
                "Implement slope drainage",
                "Remove unstable materials",
                "Plant stabilizing vegetation"
            ],
            'long_term': [
                "Regular slope monitoring",
                "Permanent stabilization structures",
                "Terracing on steep areas",
                "Professional slope maintenance"
            ],
            'cost_range': "$100,000 - $1,000,000"
        },
        'erosion': {
            'immediate': [
                "Install erosion control blankets",
                "Create temporary sediment barriers"
            ],
            'short_term': [
                "Plant ground cover vegetation",
                "Build terraces on slopes",
                "Install check dams in channels",
                "Mulch exposed soil"
            ],
            'long_term': [
                "Establish permanent vegetation",
                "Maintain erosion control structures",
                "Implement contour farming",
                "Regular monitoring and maintenance"
            ],
            'cost_range': "$20,000 - $200,000"
        },
        'seismic': {
            'immediate': [
                "Conduct seismic hazard assessment",
                "Review local building codes"
            ],
            'short_term': [
                "Design seismic-resistant foundations",
                "Use flexible building materials",
                "Install base isolators",
                "Reinforce existing structures"
            ],
            'long_term': [
                "Regular structural inspections",
                "Upgrade non-compliant structures",
                "Develop earthquake emergency plans",
                "Maintain seismic safety measures"
            ],
            'cost_range': "$75,000 - $750,000"
        },
        'drought': {
            'immediate': [
                "Water resource assessment",
                "Install rainwater collection systems"
            ],
            'short_term': [
                "Build water storage tanks",
                "Install efficient irrigation systems",
                "Implement water conservation measures",
                "Drill backup wells if feasible"
            ],
            'long_term': [
                "Develop drought-resistant landscaping",
                "Maintain water infrastructure",
                "Monitor groundwater levels",
                "Implement water recycling systems"
            ],
            'cost_range': "$30,000 - $300,000"
        },
        'wildfire': {
            'immediate': [
                "Clear immediate vegetation hazards",
                "Create defensible space (30m minimum)"
            ],
            'short_term': [
                "Install fire breaks",
                "Use fire-resistant building materials",
                "Install sprinkler systems",
                "Remove dead vegetation regularly"
            ],
            'long_term': [
                "Maintain fire breaks",
                "Regular vegetation management",
                "Fire detection systems",
                "Emergency access roads"
            ],
            'cost_range': "$40,000 - $400,000"
        },
        'subsidence': {
            'immediate': [
                "Detailed soil investigation",
                "Monitor for ground movement"
            ],
            'short_term': [
                "Design deep foundations",
                "Implement soil improvement techniques",
                "Install monitoring equipment",
                "Avoid excessive groundwater extraction"
            ],
            'long_term': [
                "Regular ground movement monitoring",
                "Maintain foundation integrity",
                "Control water table levels",
                "Professional structural inspections"
            ],
            'cost_range': "$60,000 - $600,000"
        }
    }
    
    plan = mitigation_plans.get(risk_key, {})
    
    if plan:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Immediate Actions** (0-3 months)")
            for action in plan.get('immediate', []):
                st.markdown(f"• {action}")
        
        with col2:
            st.markdown("**Short-term** (3-12 months)")
            for action in plan.get('short_term', []):
                st.markdown(f"• {action}")
        
        with col3:
            st.markdown("**Long-term** (1-5 years)")
            for action in plan.get('long_term', []):
                st.markdown(f"• {action}")
        
        st.markdown(f"\n**Estimated Cost Range:** {plan.get('cost_range', 'Contact specialists')}")


def render_mitigation_costs(risks: Dict):
    """Render estimated mitigation costs"""
    
    overall = risks.get('overall', {})
    high_count = overall.get('high_risk_count', 0)
    medium_count = overall.get('medium_risk_count', 0)
    
    # Estimate total costs
    high_risk_cost = high_count * 400000  # $400k per high risk
    medium_risk_cost = medium_count * 100000  # $100k per medium risk
    total_cost = high_risk_cost + medium_risk_cost
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "High-Risk Mitigation",
            f"${high_risk_cost:,}",
            help=f"{high_count} high-severity risks × $400,000"
        )
    
    with col2:
        st.metric(
            "Medium-Risk Mitigation",
            f"${medium_risk_cost:,}",
            help=f"{medium_count} medium-severity risks × $100,000"
        )
    
    with col3:
        st.metric(
            "Total Estimated Cost",
            f"${total_cost:,}",
            delta=f"+{(total_cost/1000000):.1f}M",
            delta_color="inverse"
        )
    
    st.info("""
    **Note:** These are rough estimates. Actual costs vary based on:
    - Site-specific conditions
    - Local labor and material costs
    - Regulatory requirements
    - Chosen mitigation strategies
    
    **Recommendation:** Consult with specialized engineers and contractors for accurate quotes.
    """)


def render_mitigation_timeline(risks: Dict):
    """Render mitigation implementation timeline"""
    
    st.markdown("""
    **Recommended Implementation Sequence:**
    
    **Phase 1 (Months 1-3): Assessment & Planning**
    - Complete all risk assessments
    - Obtain necessary permits
    - Design mitigation strategies
    - Secure financing
    
    **Phase 2 (Months 3-6): Critical Mitigation**
    - Address high-severity risks first
    - Implement immediate safety measures
    - Begin construction of permanent solutions
    
    **Phase 3 (Months 6-12): Comprehensive Implementation**
    - Complete medium-severity risk mitigation
    - Install monitoring systems
    - Implement vegetation-based solutions
    
    **Phase 4 (Years 1-5): Maintenance & Monitoring**
    - Regular inspections
    - Maintenance of mitigation structures
    - Update risk assessments annually
    - Adjust strategies as needed
    """)
    
    # Timeline visualization
    timeline_data = {
        'Phase': ['Assessment', 'Critical', 'Comprehensive', 'Maintenance'],
        'Start': [0, 3, 6, 12],
        'Duration': [3, 3, 6, 48],
        'Priority': ['High', 'Critical', 'Medium', 'Ongoing']
    }
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.timeline(
        df,
        x_start='Start',
        x_end=df['Start'] + df['Duration'],
        y='Phase',
        color='Priority',
        title='Mitigation Implementation Timeline (Months)',
        color_discrete_map={
            'Critical': '#d32f2f',
            'High': '#f57c00',
            'Medium': '#fbc02d',
            'Ongoing': '#388e3c'
        }
    )
    
    fig.update_yaxes(categoryorder='array', categoryarray=['Maintenance', 'Comprehensive', 'Critical', 'Assessment'])
    fig.update_layout(height=300)
    
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# TAB 5: COMPARISON
# ============================================================================

def render_risk_comparison(risks: Dict):
    """Render risk comparison and benchmarking"""
    
    st.markdown("## 📈 Risk Benchmarking")
    
    st.info("""
    Compare your land's risk profile against typical risk levels for different land uses.
    This helps contextualize the risks and understand if they're acceptable for your intended use.
    """)
    
    # Risk benchmark data
    benchmark_data = {
        'Risk Type': [],
        'Your Land': [],
        'Residential (Typical)': [],
        'Agricultural (Typical)': [],
        'Commercial (Typical)': []
    }
    
    risk_types = ['Flood', 'Landslide', 'Erosion', 'Seismic', 'Drought', 'Wildfire', 'Subsidence']
    typical_residential = [2, 2, 2, 3, 2, 2, 1]
    typical_agricultural = [2, 1, 3, 2, 3, 2, 1]
    typical_commercial = [2, 2, 2, 3, 2, 2, 2]
    
    for idx, risk_type in enumerate(['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']):
        risk_data = risks.get(risk_type, {})
        if risk_data:
            benchmark_data['Risk Type'].append(risk_types[idx])
            benchmark_data['Your Land'].append(risk_data.get('severity', 0))
            benchmark_data['Residential (Typical)'].append(typical_residential[idx])
            benchmark_data['Agricultural (Typical)'].append(typical_agricultural[idx])
            benchmark_data['Commercial (Typical)'].append(typical_commercial[idx])
    
    df = pd.DataFrame(benchmark_data)
    
    # Create comparison chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Your Land',
        x=df['Risk Type'],
        y=df['Your Land'],
        marker_color='#1e88e5'
    ))
    
    fig.add_trace(go.Bar(
        name='Residential (Typical)',
        x=df['Risk Type'],
        y=df['Residential (Typical)'],
        marker_color='#43a047'
    ))
    
    fig.add_trace(go.Bar(
        name='Agricultural (Typical)',
        x=df['Risk Type'],
        y=df['Agricultural (Typical)'],
        marker_color='#fb8c00'
    ))
    
    fig.add_trace(go.Bar(
        name='Commercial (Typical)',
        x=df['Risk Type'],
        y=df['Commercial (Typical)'],
        marker_color='#e53935'
    ))
    
    fig.update_layout(
        title='Risk Severity Comparison',
        xaxis_title='Risk Type',
        yaxis_title='Severity (0-5)',
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Risk acceptability assessment
    st.markdown("### ✅ Risk Acceptability Assessment")
    
    overall = risks.get('overall', {})
    avg_severity = overall.get('average_severity', 0)
    
    if avg_severity <= 2.0:
        acceptability = "✅ **LOW RISK** - Acceptable for most land uses"
        color = "success"
    elif avg_severity <= 3.0:
        acceptability = "⚠️ **MODERATE RISK** - Acceptable with standard mitigation"
        color = "info"
    elif avg_severity <= 4.0:
        acceptability = "⚠️ **ELEVATED RISK** - Requires significant mitigation"
        color = "warning"
    else:
        acceptability = "🚫 **HIGH RISK** - May not be suitable for development without extensive mitigation"
        color = "error"
    
    if color == "success":
        st.success(acceptability)
    elif color == "info":
        st.info(acceptability)
    elif color == "warning":
        st.warning(acceptability)
    else:
        st.error(acceptability)
    
    # Recommendations by land use
    st.markdown("### 🎯 Suitability by Land Use")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Residential Development**")
        residential_suitable = avg_severity <= 3.0
        if residential_suitable:
            st.success("✅ Generally Suitable")
        else:
            st.error("❌ Not Recommended")
        st.markdown(f"*Risk Level: {avg_severity:.1f}/5*")
    
    with col2:
        st.markdown("**Agricultural Use**")
        # Agriculture can tolerate higher erosion/drought but not landslide
        landslide_severity = risks.get('landslide', {}).get('severity', 0)
        ag_suitable = landslide_severity <= 3 and avg_severity <= 3.5
        if ag_suitable:
            st.success("✅ Generally Suitable")
        else:
            st.warning("⚠️ Limited Suitability")
        st.markdown(f"*Risk Level: {avg_severity:.1f}/5*")
    
    with col3:
        st.markdown("**Commercial Development**")
        commercial_suitable = avg_severity <= 2.5
        if commercial_suitable:
            st.success("✅ Generally Suitable")
        else:
            st.error("❌ Not Recommended")
        st.markdown(f"*Risk Level: {avg_severity:.1f}/5*")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_risk_color(level: str) -> str:
    """Get background color for risk level"""
    colors = {
        'very_high': '#d32f2f',
        'high': '#f57c00',
        'medium': '#fbc02d',
        'low': '#388e3c',
        'very_low': '#1b5e20',
        'unknown': '#757575'
    }
    return colors.get(level, '#757575')


def get_severity_color(severity: int) -> str:
    """Get color for severity level (1-5)"""
    if severity >= 5:
        return '#d32f2f'  # Dark red
    elif severity >= 4:
        return '#f57c00'  # Orange
    elif severity >= 3:
        return '#fbc02d'  # Yellow
    elif severity >= 2:
        return '#81c784'  # Light green
    else:
        return '#388e3c'  # Green


# ============================================================================
# EXPORT FUNCTIONALITY
# ============================================================================

def export_risk_report():
    """Export comprehensive risk report as PDF"""
    st.info("PDF export functionality coming soon!")
