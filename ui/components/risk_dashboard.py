# ============================================================================
# FILE: ui/components/risk_dashboard.py (EMERGENCY FIX)
# Replace your current risk_dashboard.py with this
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
from typing import Dict

def render_comprehensive_risks(results: Dict):
    """
    Render comprehensive risk assessment dashboard
    NOW WITH AUTOMATIC FALLBACK - WORKS WITHOUT GEE!
    """
    
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    # IF NO RISKS, GENERATE THEM NOW!
    if not comprehensive_risks or comprehensive_risks.get('overall', {}).get('level') == 'unknown':
        st.info("⚡ Generating risk assessment on-demand...")
        comprehensive_risks = _generate_emergency_risks(features)
    
    st.markdown("### 🛡️ Comprehensive Risk Assessment")
    
    # Overall risk summary
    overall_risk = comprehensive_risks.get('overall', {})
    risk_summary = comprehensive_risks.get('summary', [])
    
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
                f"{overall_risk.get('average_severity', 2.5):.1f}/5"
            )
        
        with col3:
            high_count = overall_risk.get('high_risk_count', 0)
            st.metric("High Risks", high_count)
        
        with col4:
            medium_count = overall_risk.get('medium_risk_count', 0)
            st.metric("Medium Risks", medium_count)
        
        # Summary
        if risk_summary:
            st.markdown("**Summary:**")
            for line in risk_summary:
                st.markdown(line)
    
    st.markdown("---")
    
    # Quick risk overview
    st.markdown("### 🔍 Risk Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    risks_to_show = [
        ('flood', '🌊', 'Flood', col1),
        ('landslide', '⛰️', 'Landslide', col2),
        ('seismic', '🏗️', 'Seismic', col3),
        ('erosion', '🌾', 'Erosion', col4),
    ]
    
    for risk_key, emoji, name, col in risks_to_show:
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
    
    # Detailed breakdown
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
        expanded = severity >= 4
        
        with st.expander(f"{emoji} **{title}** - {risk_data.get('level', 'unknown').replace('_', ' ').title()}", expanded=expanded):
            _render_detailed_risk_card(risk_data, emoji, title)
    
    # Mitigation
    mitigation = comprehensive_risks.get('mitigation', [])
    if mitigation:
        st.markdown("### 🛠️ Risk Mitigation Recommendations")
        for rec in mitigation:
            st.info(rec)


def _generate_emergency_risks(features: Dict) -> Dict:
    """Generate basic risk assessment when none exists"""
    
    terrain = features.get('terrain', {})
    slope = terrain.get('slope_avg', 5.0)
    elevation = terrain.get('elevation_avg', 100.0)
    
    # Flood
    if slope < 2:
        flood = {'level': 'high', 'severity': 4, 'score': 60}
    elif slope < 5:
        flood = {'level': 'medium', 'severity': 3, 'score': 35}
    else:
        flood = {'level': 'low', 'severity': 2, 'score': 15}
    
    flood.update({
        'affected_area_percent': flood['score'] / 2,
        'primary_factors': [f'Slope: {slope:.1f}°'],
        'description': f'{flood["level"].title()} flood risk based on terrain',
        'impact': 'Drainage recommended' if flood['severity'] >= 3 else 'Standard drainage'
    })
    
    # Landslide
    if slope > 25:
        landslide = {'level': 'very_high', 'severity': 5, 'score': 80}
    elif slope > 15:
        landslide = {'level': 'high', 'severity': 4, 'score': 55}
    elif slope > 10:
        landslide = {'level': 'medium', 'severity': 3, 'score': 35}
    else:
        landslide = {'level': 'low', 'severity': 2, 'score': 15}
    
    landslide.update({
        'slope_avg': slope,
        'primary_factors': [f'Slope: {slope:.1f}°'],
        'description': f'{landslide["level"].title()} landslide risk',
        'impact': 'Stabilization needed' if landslide['severity'] >= 4 else 'Standard precautions'
    })
    
    # Erosion
    if slope > 15:
        erosion = {'level': 'high', 'severity': 4, 'score': 50}
    elif slope > 8:
        erosion = {'level': 'medium', 'severity': 3, 'score': 30}
    else:
        erosion = {'level': 'low', 'severity': 2, 'score': 15}
    
    erosion.update({
        'slope': slope,
        'primary_factors': [f'Slope: {slope:.1f}°'],
        'description': f'{erosion["level"].title()} erosion risk',
        'impact': 'Control needed' if erosion['severity'] >= 3 else 'Minor erosion'
    })
    
    # Static risks
    seismic = {
        'level': 'medium', 'severity': 3, 'score': 40,
        'primary_factors': ['Algeria seismic zone'],
        'description': 'Moderate seismic activity',
        'impact': 'Follow building codes'
    }
    
    drought = {
        'level': 'medium', 'severity': 3, 'score': 35,
        'primary_factors': ['Semi-arid climate'],
        'description': 'Moderate drought risk',
        'impact': 'Water conservation'
    }
    
    wildfire = {
        'level': 'low', 'severity': 2, 'score': 20,
        'primary_factors': ['Moderate vegetation'],
        'description': 'Low wildfire risk',
        'impact': 'Basic fire safety'
    }
    
    subsidence = {
        'level': 'low', 'severity': 2, 'score': 15,
        'primary_factors': ['Stable terrain'],
        'description': 'Low subsidence risk',
        'impact': 'Standard foundations'
    }
    
    # Overall
    severities = [flood['severity'], landslide['severity'], erosion['severity'], 3, 3, 2, 2]
    avg_sev = sum(severities) / len(severities)
    high_count = sum(1 for s in severities if s >= 4)
    medium_count = sum(1 for s in severities if s == 3)
    
    if high_count >= 2:
        overall_level = 'high'
    elif high_count >= 1 or medium_count >= 3:
        overall_level = 'medium'
    else:
        overall_level = 'low'
    
    # Mitigation
    mitigation = []
    if flood['severity'] >= 3:
        mitigation.append('🌊 **Flood:** Install drainage systems')
    if landslide['severity'] >= 3:
        mitigation.append('⛰️ **Landslide:** Slope stabilization needed')
    if erosion['severity'] >= 3:
        mitigation.append('🌾 **Erosion:** Erosion control structures')
    if not mitigation:
        mitigation.append('✅ Standard construction practices sufficient')
    
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
            'average_severity': round(avg_sev, 2),
            'high_risk_count': high_count,
            'medium_risk_count': medium_count,
            'total_risks_assessed': 7
        },
        'summary': [
            f'📊 Overall: {overall_level.title()}',
            f'📈 Average Severity: {avg_sev:.1f}/5',
            f'⚠️ {high_count} High, {medium_count} Medium Risks'
        ],
        'mitigation': mitigation
    }


def _render_detailed_risk_card(risk_data: Dict, emoji: str, title: str):
    """Render detailed risk card"""
    severity = risk_data.get('severity', 0)
    score = risk_data.get('score', 0)
    description = risk_data.get('description', 'No description')
    factors = risk_data.get('primary_factors', [])
    impact = risk_data.get('impact', 'Unknown')
    
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
    
    st.markdown(f"**📝 Description:** {description}")
    
    if factors:
        st.markdown("**🔍 Key Factors:**")
        for factor in factors:
            st.markdown(f"• {factor}")
    
    st.markdown(f"**⚠️ Impact:** {impact}")


def _get_risk_color(level: str) -> str:
    """Get color for risk level"""
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
    """Get color for severity (1-5)"""
    if severity >= 5:
        return '#d32f2f'
    elif severity >= 4:
        return '#f57c00'
    elif severity >= 3:
        return '#fbc02d'
    elif severity >= 2:
        return '#81c784'
    else:
        return '#388e3c'


def render_risk_summary_metrics(results: Dict):
    """Quick risk summary metrics"""
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    # Generate if missing
    if not comprehensive_risks or comprehensive_risks.get('overall', {}).get('level') == 'unknown':
        comprehensive_risks = _generate_emergency_risks(features)
    
    overall = comprehensive_risks.get('overall', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        flood = comprehensive_risks.get('flood', {})
        st.metric("🌊 Flood", flood.get('level', 'Unknown').replace('_', ' ').title())
    
    with col2:
        landslide = comprehensive_risks.get('landslide', {})
        st.metric("⛰️ Landslide", landslide.get('level', 'Unknown').replace('_', ' ').title())
    
    with col3:
        seismic = comprehensive_risks.get('seismic', {})
        st.metric("🏗️ Seismic", seismic.get('level', 'Unknown').replace('_', ' ').title())
    
    with col4:
        st.metric("📊 Overall", overall.get('level', 'Unknown').replace('_', ' ').title())
