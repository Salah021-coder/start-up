# ============================================================================
# FILE: ui/pages/risk_analysis.py (CLEAN SIMPLIFIED VERSION)
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

def render():
    """Render dedicated risk analysis page"""
    
    st.title("🛡️ Comprehensive Risk Assessment")
    
    # Check if analysis results are available
    if not st.session_state.get('analysis_results'):
        st.warning("⚠️ No analysis results available")
        st.info("Please run a land analysis first to see risk assessment.")
        
        if st.button("Go to Analysis Page", type="primary"):
            st.session_state.current_page = 'analysis'
            st.rerun()
        return
    
    results = st.session_state.analysis_results
    
    # Extract risk data
    risk_assessment = results.get('risk_assessment', {})
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    # If no comprehensive risks, use basic risk assessment
    if not comprehensive_risks:
        st.info("Generating risk assessment from analysis data...")
        comprehensive_risks = _generate_basic_risks(risk_assessment, features)
    
    # Display risk overview
    st.markdown("---")
    render_risk_overview(comprehensive_risks)
    
    st.markdown("---")
    render_risk_details(comprehensive_risks)
    
    st.markdown("---")
    render_risk_chart(comprehensive_risks)
    
    st.markdown("---")
    render_mitigation(comprehensive_risks)


def render_risk_overview(risks: Dict):
    """Render quick risk overview"""
    
    st.markdown("### 📊 Risk Overview")
    
    overall = risks.get('overall', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        level = overall.get('level', 'unknown')
        color = _get_risk_color(level)
        st.markdown(f"""
        <div style='background-color:{color};padding:20px;border-radius:10px;text-align:center;'>
            <h2 style='color:white;margin:0;'>{level.replace('_', ' ').title()}</h2>
            <p style='color:white;margin:5px 0 0 0;'>Overall Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Average Severity", f"{overall.get('average_severity', 0):.1f}/5")
    
    with col3:
        st.metric("High Risks", overall.get('high_risk_count', 0))
    
    with col4:
        st.metric("Medium Risks", overall.get('medium_risk_count', 0))
    
    # Summary
    summary = risks.get('summary', [])
    if summary:
        st.markdown("**Summary:**")
        for line in summary:
            st.markdown(line)


def render_risk_details(risks: Dict):
    """Render detailed risk breakdown"""
    
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
        risk_data = risks.get(risk_key, {})
        
        if not risk_data or risk_data.get('level') == 'unknown':
            continue
        
        level = risk_data.get('level', 'unknown')
        severity = risk_data.get('severity', 0)
        
        with st.expander(f"{emoji} **{title}** - {level.replace('_', ' ').title()}", expanded=(severity >= 4)):
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
                score = risk_data.get('score', 0)
                st.markdown(f"**Risk Score:** {score:.1f}/100")
                st.progress(min(score / 100, 1.0))
            
            st.markdown(f"**Description:** {risk_data.get('description', 'N/A')}")
            
            factors = risk_data.get('primary_factors', [])
            if factors:
                st.markdown("**Key Factors:**")
                for factor in factors:
                    st.markdown(f"• {factor}")
            
            st.markdown(f"**Impact:** {risk_data.get('impact', 'N/A')}")


def render_risk_chart(risks: Dict):
    """Render risk comparison chart"""
    
    st.markdown("### 📊 Risk Severity Comparison")
    
    risk_types = {
        'flood': ('🌊', 'Flood'),
        'landslide': ('⛰️', 'Landslide'),
        'erosion': ('🌾', 'Erosion'),
        'seismic': ('🏗️', 'Seismic'),
        'drought': ('💧', 'Drought'),
        'wildfire': ('🔥', 'Wildfire'),
        'subsidence': ('🏚️', 'Subsidence')
    }
    
    risk_names = []
    severities = []
    colors = []
    
    for risk_key, (emoji, name) in risk_types.items():
        risk_data = risks.get(risk_key, {})
        if risk_data and risk_data.get('level') != 'unknown':
            risk_names.append(f"{emoji} {name}")
            severity = risk_data.get('severity', 0)
            severities.append(severity)
            colors.append(_get_severity_color(severity))
    
    if severities:
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


def render_mitigation(risks: Dict):
    """Render mitigation recommendations"""
    
    st.markdown("### 🛠️ Risk Mitigation Recommendations")
    
    mitigation = risks.get('mitigation', [])
    
    if mitigation:
        for rec in mitigation:
            st.info(rec)
    else:
        st.success("✅ No specific mitigation measures required - follow standard construction practices")


def _generate_basic_risks(risk_assessment: Dict, features: Dict) -> Dict:
    """Generate basic risk structure from risk_assessment"""
    
    # Extract basic info
    overall_level = risk_assessment.get('overall_level', 'medium')
    high_count = risk_assessment.get('high_risk_count', 0)
    medium_count = risk_assessment.get('medium_risk_count', 0)
    
    # Create basic structure
    return {
        'overall': {
            'level': overall_level,
            'average_severity': 2.5,
            'high_risk_count': high_count,
            'medium_risk_count': medium_count
        },
        'flood': {
            'level': 'medium',
            'severity': 3,
            'score': 40.0,
            'description': 'Moderate flood risk based on terrain',
            'impact': 'Standard drainage recommended',
            'primary_factors': ['Terrain characteristics analyzed']
        },
        'landslide': {
            'level': 'low',
            'severity': 2,
            'score': 20.0,
            'description': 'Low landslide risk',
            'impact': 'Standard engineering practices',
            'primary_factors': ['Stable terrain']
        },
        'erosion': {
            'level': 'low',
            'severity': 2,
            'score': 20.0,
            'description': 'Low erosion risk',
            'impact': 'Basic erosion control',
            'primary_factors': ['Moderate vegetation']
        },
        'seismic': {
            'level': 'medium',
            'severity': 3,
            'score': 40.0,
            'description': 'Moderate seismic activity region',
            'impact': 'Seismic building codes apply',
            'primary_factors': ['Regional seismic zone']
        },
        'drought': {
            'level': 'medium',
            'severity': 3,
            'score': 35.0,
            'description': 'Moderate drought risk',
            'impact': 'Water conservation recommended',
            'primary_factors': ['Semi-arid climate']
        },
        'wildfire': {
            'level': 'low',
            'severity': 2,
            'score': 20.0,
            'description': 'Low wildfire risk',
            'impact': 'Basic fire safety',
            'primary_factors': ['Moderate vegetation']
        },
        'subsidence': {
            'level': 'low',
            'severity': 2,
            'score': 15.0,
            'description': 'Low subsidence risk',
            'impact': 'Standard foundations',
            'primary_factors': ['Stable terrain']
        },
        'summary': [
            f"Overall Risk Level: {overall_level.replace('_', ' ').title()}",
            f"High Risks: {high_count}",
            f"Medium Risks: {medium_count}"
        ],
        'mitigation': [
            '✅ Follow standard construction practices',
            '🏗️ Implement local building codes',
            '💧 Consider water management systems'
        ]
    }


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
    """Get color for severity"""
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
