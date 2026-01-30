# ============================================================================
# FILE: ui/pages/results.py (UPDATED WITH COMPREHENSIVE RISK DISPLAY)
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import numpy as np
from typing import Dict


def render():
    """Render enhanced results page with comprehensive risk assessment"""
    
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
    risk_quality = data_sources.get('risk_assessment', 'unknown')
    
    col1, col2 = st.columns(2)
    with col1:
        if infra_quality == 'real_osm':
            st.success("✅ Real OpenStreetMap data used for infrastructure")
        else:
            st.info("ℹ️ Estimated data used for infrastructure")
    
    with col2:
        if 'Comprehensive' in risk_quality:
            st.success("✅ Comprehensive risk assessment (7 risk types)")
        else:
            st.info("ℹ️ Basic risk assessment (flood only)")
    
    # Summary metrics
    render_summary_metrics(results)
    
    st.markdown("---")
    
    # === NEW: COMPREHENSIVE RISK ASSESSMENT SECTION ===
    render_comprehensive_risk_section(results)
    
    st.markdown("---")
    
    # Location and accessibility summary
    render_location_summary(results)
    
    st.markdown("---")
    
    # Analysis map
    render_analysis_map(results)
    
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


def render_comprehensive_risk_section(results: Dict):
    """
    Display comprehensive risk assessment - NOW WITH AUTO-GENERATION!
    """
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    # ========== AUTO-GENERATE IF MISSING ==========
    if not comprehensive_risks or not comprehensive_risks.get('overall'):
        st.info("⚡ Generating risk assessment from terrain data...")
        comprehensive_risks = _auto_generate_risks(features)
        # Store it back
        if 'environmental' not in features:
            features['environmental'] = {}
        features['environmental']['comprehensive_risks'] = comprehensive_risks
    
    st.markdown("## 🛡️ Comprehensive Risk Assessment")
    
    # Overall risk profile
    overall_risk = comprehensive_risks.get('overall', {})
    
    with st.expander("📊 Overall Risk Profile", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            level = overall_risk.get('level', 'medium')
            color = _get_risk_color(level)
            st.markdown(f"""
            <div style='background-color:{color};padding:20px;border-radius:10px;text-align:center;'>
                <h2 style='color:white;margin:0;'>{level.replace('_', ' ').title()}</h2>
                <p style='color:white;margin:5px 0 0 0;'>Overall Risk</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "Average Severity", 
                f"{overall_risk.get('average_severity', 2.5):.1f}/5",
                help="Average severity across all risk types"
            )
        
        with col3:
            high_count = overall_risk.get('high_risk_count', 0)
            st.metric(
                "High Risks", 
                high_count,
                delta="Critical" if high_count > 0 else "None"
            )
        
        with col4:
            medium_count = overall_risk.get('medium_risk_count', 0)
            st.metric(
                "Medium Risks", 
                medium_count
            )
        
        # Summary text
        summary = comprehensive_risks.get('summary', [])
        if summary:
            st.markdown("**Summary:**")
            for line in summary:
                st.markdown(line)
    
    # Quick risk overview cards
    st.markdown("### 🔍 Risk Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    risk_quick_view = [
        ('flood', '🌊', 'Flood', col1),
        ('landslide', '⛰️', 'Landslide', col2),
        ('seismic', '🏗️', 'Seismic', col3),
        ('erosion', '🌾', 'Erosion', col4),
    ]
    
    for risk_key, emoji, name, col in risk_quick_view:
        risk_data = comprehensive_risks.get(risk_key, {})
        if risk_data:
            with col:
                level = risk_data.get('level', 'unknown')
                severity = risk_data.get('severity', 0)
                color = _get_severity_color(severity)
                
                st.markdown(f"""
                <div style='background-color:{color};padding:10px;border-radius:8px;text-align:center;'>
                    <p style='font-size:24px;margin:0;'>{emoji}</p>
                    <p style='font-weight:bold;margin:5px 0;'>{name}</p>
                    <p style='margin:0;font-size:14px;'>{level.replace('_', ' ').title()}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Second row
    col1, col2, col3 = st.columns(3)
    
    risk_quick_view_2 = [
        ('drought', '💧', 'Drought', col1),
        ('wildfire', '🔥', 'Wildfire', col2),
        ('subsidence', '🏚️', 'Subsidence', col3),
    ]
    
    for risk_key, emoji, name, col in risk_quick_view_2:
        risk_data = comprehensive_risks.get(risk_key, {})
        if risk_data:
            with col:
                level = risk_data.get('level', 'unknown')
                severity = risk_data.get('severity', 0)
                color = _get_severity_color(severity)
                
                st.markdown(f"""
                <div style='background-color:{color};padding:10px;border-radius:8px;text-align:center;'>
                    <p style='font-size:24px;margin:0;'>{emoji}</p>
                    <p style='font-weight:bold;margin:5px 0;'>{name}</p>
                    <p style='margin:0;font-size:14px;'>{level.replace('_', ' ').title()}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed risk breakdown
    st.markdown("### 📋 Detailed Risk Analysis")
    
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
        risk_data = comprehensive_risks.get(risk_key, {})
        
        if not risk_data or risk_data.get('level') == 'unknown':
            continue
        
        severity = risk_data.get('severity', 0)
        level = risk_data.get('level', 'unknown')
        
        # Expand high-risk items by default
        expanded = severity >= 4
        
        with st.expander(f"{emoji} **{title}** - {level.replace('_', ' ').title()}", expanded=expanded):
            _render_detailed_risk_card(risk_data, emoji, title)
    
    # Risk severity chart
    st.markdown("### 📊 Risk Severity Comparison")
    _render_risk_severity_chart(comprehensive_risks, risk_types)
    
    st.markdown("---")
    
    # Mitigation recommendations
    mitigation = comprehensive_risks.get('mitigation', [])
    if mitigation:
        st.markdown("### 🛠️ Risk Mitigation Recommendations")
        
        for recommendation in mitigation:
            st.info(recommendation)


def _auto_generate_risks(features: Dict) -> Dict:
    """
    Auto-generate comprehensive risk assessment from terrain data
    This runs when GEE data is not available
    """
    terrain = features.get('terrain', {})
    slope = terrain.get('slope_avg', 5.0)
    elevation = terrain.get('elevation_avg', 100.0)
    slope_max = terrain.get('slope_max', slope * 1.5)
    
    # === FLOOD RISK (based on slope - flat = high flood risk) ===
    if slope < 2:
        flood = {'level': 'high', 'severity': 4, 'score': 65.0}
    elif slope < 5:
        flood = {'level': 'medium', 'severity': 3, 'score': 35.0}
    elif slope < 10:
        flood = {'level': 'low', 'severity': 2, 'score': 15.0}
    else:
        flood = {'level': 'very_low', 'severity': 1, 'score': 5.0}
    
    flood.update({
        'water_occurrence': 0,
        'affected_area_percent': flood['score'] / 2,
        'primary_factors': [
            f"Terrain slope: {slope:.1f}° ({'poor' if slope < 3 else 'good'} drainage)"
        ],
        'description': f'{flood["level"].replace("_", " ").title()} flood risk based on terrain analysis',
        'impact': 'Drainage infrastructure required' if flood['severity'] >= 3 else 'Standard drainage sufficient'
    })
    
    # === LANDSLIDE RISK (based on slope steepness) ===
    if slope > 25:
        landslide = {'level': 'very_high', 'severity': 5, 'score': 85.0}
    elif slope > 15:
        landslide = {'level': 'high', 'severity': 4, 'score': 60.0}
    elif slope > 10:
        landslide = {'level': 'medium', 'severity': 3, 'score': 35.0}
    elif slope > 5:
        landslide = {'level': 'low', 'severity': 2, 'score': 15.0}
    else:
        landslide = {'level': 'very_low', 'severity': 1, 'score': 5.0}
    
    landslide.update({
        'slope_avg': slope,
        'slope_max': slope_max,
        'elevation_range': 0,
        'primary_factors': [
            f"Average slope: {slope:.1f}°",
            f"Maximum slope: {slope_max:.1f}°"
        ],
        'description': f'{landslide["level"].replace("_", " ").title()} landslide risk',
        'impact': 'Slope stabilization essential' if landslide['severity'] >= 4 else 'Standard engineering sufficient'
    })
    
    # === EROSION RISK (based on slope) ===
    if slope > 15:
        erosion = {'level': 'high', 'severity': 4, 'score': 55.0}
    elif slope > 8:
        erosion = {'level': 'medium', 'severity': 3, 'score': 35.0}
    elif slope > 3:
        erosion = {'level': 'low', 'severity': 2, 'score': 15.0}
    else:
        erosion = {'level': 'very_low', 'severity': 1, 'score': 5.0}
    
    erosion.update({
        'slope': slope,
        'vegetation_cover': 0.5,
        'primary_factors': [
            f"Slope: {slope:.1f}° (erosion {'likely' if slope > 10 else 'minimal'})"
        ],
        'description': f'{erosion["level"].replace("_", " ").title()} erosion risk',
        'impact': 'Erosion control structures needed' if erosion['severity'] >= 3 else 'Minor erosion control sufficient'
    })
    
    # === SEISMIC RISK (Algeria baseline - moderate) ===
    seismic = {
        'level': 'medium',
        'severity': 3,
        'score': 40.0,
        'seismic_zone': 'II-III',
        'latitude': 36.0,
        'longitude': 5.0,
        'primary_factors': [
            'Located in Algeria (moderate seismic activity)',
            'Seismic building codes apply'
        ],
        'description': 'Moderate seismic activity region',
        'impact': 'Seismic-resistant design required per building codes'
    }
    
    # === DROUGHT RISK (Algeria semi-arid baseline) ===
    drought = {
        'level': 'medium',
        'severity': 3,
        'score': 35.0,
        'latitude': 36.0,
        'vegetation_health': 0.5,
        'primary_factors': [
            'Semi-arid climate zone',
            'Water conservation recommended'
        ],
        'description': 'Moderate drought risk - semi-arid region',
        'impact': 'Water storage and conservation systems recommended'
    }
    
    # === WILDFIRE RISK (low baseline) ===
    wildfire = {
        'level': 'low',
        'severity': 2,
        'score': 20.0,
        'vegetation_density': 0.5,
        'slope': slope,
        'primary_factors': [
            'Moderate vegetation density',
            'Standard fire safety measures'
        ],
        'description': 'Low wildfire risk under normal conditions',
        'impact': 'Basic fire safety measures sufficient'
    }
    
    # === SUBSIDENCE RISK (low baseline) ===
    subsidence = {
        'level': 'low',
        'severity': 2,
        'score': 15.0,
        'elevation': elevation,
        'slope': slope,
        'primary_factors': [
            'Stable terrain characteristics',
            'No obvious subsidence indicators'
        ],
        'description': 'Low subsidence risk',
        'impact': 'Standard foundation practices sufficient'
    }
    
    # === CALCULATE OVERALL ===
    all_risks = [flood, landslide, erosion, seismic, drought, wildfire, subsidence]
    severities = [r['severity'] for r in all_risks]
    avg_severity = sum(severities) / len(severities)
    
    high_count = sum(1 for s in severities if s >= 4)
    medium_count = sum(1 for s in severities if s == 3)
    low_count = sum(1 for s in severities if s <= 2)
    
    # Determine overall level
    if high_count >= 3 or avg_severity >= 4.0:
        overall_level = 'very_high'
    elif high_count >= 2 or avg_severity >= 3.5:
        overall_level = 'high'
    elif high_count >= 1 or medium_count >= 3:
        overall_level = 'medium'
    elif medium_count >= 1:
        overall_level = 'low'
    else:
        overall_level = 'very_low'
    
    # === GENERATE SUMMARY ===
    summary = []
    
    major_risks = [r for r in [
        ('Flood', flood), ('Landslide', landslide), ('Erosion', erosion),
        ('Seismic', seismic), ('Drought', drought), ('Wildfire', wildfire)
    ] if r[1]['severity'] >= 4]
    
    if major_risks:
        risk_names = ', '.join([f"{name} ({data['level'].replace('_', ' ').title()})" 
                                for name, data in major_risks])
        summary.append(f"⚠️ **High Risks:** {risk_names}")
    else:
        summary.append("✅ **No high-severity risks identified**")
    
    summary.append(f"📊 **Overall Risk Level:** {overall_level.replace('_', ' ').title()}")
    summary.append(f"📈 **Average Severity:** {avg_severity:.1f}/5")
    summary.append(f"🔍 **Risk Distribution:** {high_count} High, {medium_count} Medium, {low_count} Low")
    
    # === GENERATE MITIGATION ===
    mitigation = []
    
    if flood['severity'] >= 3:
        mitigation.append('🌊 **Flood:** Install comprehensive drainage systems, consider elevation')
    if landslide['severity'] >= 3:
        mitigation.append('⛰️ **Landslide:** Slope stabilization, retaining walls required')
    if erosion['severity'] >= 3:
        mitigation.append('🌾 **Erosion:** Install erosion control structures, vegetation cover')
    if seismic['severity'] >= 3:
        mitigation.append('🏗️ **Seismic:** Follow seismic building codes, flexible foundations')
    
    if not mitigation:
        mitigation.append('✅ **Standard Practices:** No major mitigation required - follow standard construction practices')
    
    # === RETURN COMPLETE ASSESSMENT ===
    return {
        'flood': flood,
        'landslide': landslide,
        'erosion': erosion,
        'seismic': seismic,
        'drought': drought,
        'wildfire': wildfire,
        'subsidence': subsidence,
        'overall': {
            'level': overall_level,
            'average_severity': round(avg_severity, 2),
            'high_risk_count': high_count,
            'medium_risk_count': medium_count,
            'total_risks_assessed': 7
        },
        'summary': summary,
        'mitigation': mitigation
    }

def _render_detailed_risk_card(risk_data: Dict, emoji: str, title: str):
    """Render detailed information for a specific risk"""
    
    severity = risk_data.get('severity', 0)
    score = risk_data.get('score', 0)
    description = risk_data.get('description', 'No description available')
    factors = risk_data.get('primary_factors', [])
    impact = risk_data.get('impact', 'Impact unknown')
    
    # Severity display
    col1, col2 = st.columns([1, 3])
    
    with col1:
        color = _get_severity_color(severity)
        st.markdown(f"""
        <div style='background-color:{color};padding:15px;border-radius:8px;text-align:center;'>
            <h3 style='color:white;margin:0;'>{severity}/5</h3>
            <p style='color:white;margin:5px 0 0 0;font-size:12px;'>Severity</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**Risk Score:** {score:.1f}/100")
        st.progress(min(score / 100, 1.0))
    
    # Description
    st.markdown(f"**📝 Description:** {description}")
    
    # Primary factors
    if factors:
        st.markdown("**🔍 Key Factors:**")
        for factor in factors:
            st.markdown(f"• {factor}")
    
    # Impact
    st.markdown(f"**⚠️ Potential Impact:** {impact}")


def _render_risk_severity_chart(risks: Dict, risk_types: list):
    """Render horizontal bar chart comparing all risk severities"""
    
    risk_names = []
    severities = []
    colors = []
    
    for risk_key, emoji, title in risk_types:
        risk_data = risks.get(risk_key, {})
        
        if risk_data and risk_data.get('level') != 'unknown':
            risk_names.append(f"{emoji} {title.replace(' Risk', '')}")
            severity = risk_data.get('severity', 0)
            severities.append(severity)
            colors.append(_get_severity_color(severity))
    
    if not severities:
        st.info("No risk data available for chart")
        return
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=severities,
            y=risk_names,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{s}/5" for s in severities],
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


def _get_risk_color(level: str) -> str:
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


def _get_severity_color(severity: int) -> str:
    """Get color for severity level (1-5)"""
    if severity >= 5:
        return '#d32f2f'  # Red
    elif severity >= 4:
        return '#f57c00'  # Orange
    elif severity >= 3:
        return '#fbc02d'  # Yellow
    elif severity >= 2:
        return '#81c784'  # Light green
    else:
        return '#388e3c'  # Green

def metric_card(title, value, delta=None):
    delta_html = ""
    if delta is not None:
        color = "#22c55e" if delta.startswith("+") else "#ef4444"
        delta_html = f"""
        <div style="
            margin-top:6px;
            font-size:14px;
            color:{color};
            font-weight:600;
        ">
            {delta}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #0f172a, #020617);
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 18px;
            height: 120px;
            box-shadow: 0 10px 25px rgba(0,0,0,.35);
        ">
            <div style="color:#94a3b8;font-size:13px;">
                {title}
            </div>
            <div style="
                color:white;
                font-size:34px;
                font-weight:700;
                margin-top:6px;
            ">
                {value}
            </div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_summary_metrics(results):

    st.markdown("### 📈 Summary Metrics")

    col1, col2, col3, col4 = st.columns(4)

    score = results.get('overall_score', 0)
    delta = f"+{(score-5):.1f}" if score > 5 else f"{(score-5):.1f}"

    with col1:
        metric_card("Overall Score", f"{score:.1f}/10", delta)

    with col2:
        confidence = results.get('confidence_level', 0) * 100
        metric_card("Confidence", f"{confidence:.0f}%")

    with col3:
        risk = results.get('risk_assessment', {}).get('level', 'Medium')
        metric_card("Risk Level", risk)

    with col4:
        area = results.get('boundary', {}).get('area_hectares', 0)
        metric_card("Area", f"{area:.2f} ha")



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


def render_analysis_map(results):
    """Render analysis map (placeholder)"""
    st.markdown("### 🗺️ Location Map")
    
    boundary = results.get('boundary', {})
    centroid = boundary.get('centroid', [5.41, 36.19])
    
    # Create map
    m = folium.Map(location=[centroid[1], centroid[0]], zoom_start=14)
    
    # Add boundary if available
    geojson = boundary.get('geojson')
    if geojson:
        folium.GeoJson(
            geojson,
            style_function=lambda x: {
                'fillColor': 'blue',
                'color': 'blue',
                'weight': 2,
                'fillOpacity': 0.3
            }
        ).add_to(m)
    
    st_folium(m, width=800, height=400)


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
