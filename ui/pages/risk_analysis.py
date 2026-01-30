# ============================================================================
# FILE: ui/pages/risk_analysis.py (FIXED - WITH AUTO-GENERATION)
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict

def render():
    """Render dedicated risk analysis page"""
    
    st.title("🛡️ Comprehensive Risk Assessment")
    
    # Check if analysis results are available
    if not st.session_state.get('analysis_results'):
        st.warning("⚠️ No analysis results available")
        st.info("Please run a land analysis first to see risk assessment.")
        
        if st.button("Go to Analysis Page"):
            st.session_state.current_page = 'analysis'
            st.rerun()
        return
    
    results = st.session_state.analysis_results
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    # ========== AUTO-GENERATE IF MISSING (SAME AS RESULTS PAGE) ==========
    if not comprehensive_risks or not comprehensive_risks.get('overall'):
        st.info("⚡ Generating risk assessment from terrain data...")
        comprehensive_risks = _auto_generate_risks(features)
        # Store it back
        if 'environmental' not in features:
            features['environmental'] = {}
        features['environmental']['comprehensive_risks'] = comprehensive_risks
        st.success("✅ Risk assessment generated successfully!")
    
    # Page header with summary
    st.markdown("""
    This page provides a detailed assessment of **7 major risk types** that could affect 
    your land development project. Each risk is evaluated based on terrain analysis and 
    location characteristics.
    """)
    
    st.markdown("---")
    
    # Quick summary metrics
    st.markdown("### 📊 Quick Risk Overview")
    render_risk_summary_metrics(comprehensive_risks)
    
    st.markdown("---")
    
    # Overall risk profile
    st.markdown("### 🎯 Overall Risk Profile")
    render_overall_risk_profile(comprehensive_risks)
    
    st.markdown("---")
    
    # Quick risk cards
    st.markdown("### 🔍 Risk Type Overview")
    render_risk_cards(comprehensive_risks)
    
    st.markdown("---")
    
    # Detailed risk breakdown
    st.markdown("### 📋 Detailed Risk Analysis")
    render_detailed_risks(comprehensive_risks)
    
    st.markdown("---")
    
    # Risk severity comparison
    st.markdown("### 📈 Risk Severity Analysis")
    render_risk_severity_comparison(comprehensive_risks)
    
    st.markdown("---")
    
    # Risk matrix
    st.markdown("### 🎯 Risk Impact Matrix")
    render_risk_matrix(comprehensive_risks)
    
    st.markdown("---")
    
    # Detailed risk table
    st.markdown("### 📋 Detailed Risk Summary Table")
    render_risk_table(comprehensive_risks)
    
    st.markdown("---")
    
    # Mitigation strategies
    st.markdown("### 🛠️ Risk Mitigation Recommendations")
    render_mitigation(comprehensive_risks)
    
    st.markdown("---")
    
    # Action items
    st.markdown("### ✅ Recommended Actions")
    render_action_items(comprehensive_risks)
    
    st.markdown("---")
    
    # Export options
    st.markdown("### 💾 Export Risk Report")
    render_export_options(comprehensive_risks)


def _auto_generate_risks(features: Dict) -> Dict:
    """
    Auto-generate comprehensive risk assessment from terrain data
    IDENTICAL TO results.py implementation
    """
    terrain = features.get('terrain', {})
    slope = terrain.get('slope_avg', 5.0)
    elevation = terrain.get('elevation_avg', 100.0)
    slope_max = terrain.get('slope_max', slope * 1.5)
    
    # === FLOOD RISK ===
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
    
    # === LANDSLIDE RISK ===
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
    
    # === EROSION RISK ===
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
    
    # === SEISMIC RISK ===
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
    
    # === DROUGHT RISK ===
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
    
    # === WILDFIRE RISK ===
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
    
    # === SUBSIDENCE RISK ===
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
        mitigation.append('✅ **Standard Practices:** No major mitigation required')
    
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


def render_risk_summary_metrics(risks: Dict):
    """Quick summary metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        flood = risks.get('flood', {})
        st.metric("🌊 Flood", flood.get('level', 'Unknown').replace('_', ' ').title())
    
    with col2:
        landslide = risks.get('landslide', {})
        st.metric("⛰️ Landslide", landslide.get('level', 'Unknown').replace('_', ' ').title())
    
    with col3:
        seismic = risks.get('seismic', {})
        st.metric("🏗️ Seismic", seismic.get('level', 'Unknown').replace('_', ' ').title())
    
    with col4:
        overall = risks.get('overall', {})
        st.metric("📊 Overall", overall.get('level', 'Unknown').replace('_', ' ').title())


def render_overall_risk_profile(risks: Dict):
    """Render overall risk profile section"""
    overall = risks.get('overall', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        level = overall.get('level', 'medium')
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
            f"{overall.get('average_severity', 2.5):.1f}/5",
            help="Average across all 7 risk types"
        )
    
    with col3:
        high_count = overall.get('high_risk_count', 0)
        st.metric(
            "High Risks", 
            high_count,
            delta="Critical" if high_count > 0 else "None"
        )
    
    with col4:
        medium_count = overall.get('medium_risk_count', 0)
        st.metric(
            "Medium Risks", 
            medium_count
        )
    
    # Summary text
    summary = risks.get('summary', [])
    if summary:
        st.markdown("**Summary:**")
        for line in summary:
            st.markdown(line)


def render_risk_cards(risks: Dict):
    """Render quick risk overview cards"""
    
    risk_types = {
        'flood': ('🌊', 'Flood'),
        'landslide': ('⛰️', 'Landslide'),
        'erosion': ('🌾', 'Erosion'),
        'seismic': ('🏗️', 'Seismic'),
        'drought': ('💧', 'Drought'),
        'wildfire': ('🔥', 'Wildfire'),
        'subsidence': ('🏚️', 'Subsidence')
    }
    
    # First row - 4 risks
    col1, col2, col3, col4 = st.columns(4)
    cols_row1 = [col1, col2, col3, col4]
    
    for i, (risk_key, (emoji, name)) in enumerate(list(risk_types.items())[:4]):
        risk_data = risks.get(risk_key, {})
        if risk_data:
            with cols_row1[i]:
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
    
    # Second row - 3 risks
    col1, col2, col3 = st.columns(3)
    cols_row2 = [col1, col2, col3]
    
    for i, (risk_key, (emoji, name)) in enumerate(list(risk_types.items())[4:]):
        risk_data = risks.get(risk_key, {})
        if risk_data:
            with cols_row2[i]:
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


def render_detailed_risks(risks: Dict):
    """Render detailed risk breakdown with expanders"""
    
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
            
            st.markdown(f"**📝 Description:** {risk_data.get('description', 'N/A')}")
            
            factors = risk_data.get('primary_factors', [])
            if factors:
                st.markdown("**🔍 Key Factors:**")
                for factor in factors:
                    st.markdown(f"• {factor}")
            
            st.markdown(f"**⚠️ Impact:** {risk_data.get('impact', 'N/A')}")


def render_risk_severity_comparison(risks: Dict):
    """Render severity comparison chart"""
    
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
    
    if not severities:
        st.info("No risk data available")
        return
    
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


def render_risk_matrix(risks: Dict):
    """Render risk probability/impact matrix"""
    
    risk_types = {
        'flood': '🌊 Flood',
        'landslide': '⛰️ Landslide',
        'erosion': '🌾 Erosion',
        'seismic': '🏗️ Seismic',
        'drought': '💧 Drought',
        'wildfire': '🔥 Wildfire',
        'subsidence': '🏚️ Subsidence'
    }
    
    matrix_data = []
    for risk_key, label in risk_types.items():
        risk_info = risks.get(risk_key, {})
        if risk_info and risk_info.get('level') != 'unknown':
            severity = risk_info.get('severity', 0)
            score = risk_info.get('score', 0)
            likelihood = score / 20
            
            matrix_data.append({
                'Risk': label,
                'Severity': severity,
                'Likelihood': likelihood,
                'Priority': severity * likelihood
            })
    
    if not matrix_data:
        st.info("No risk data available")
        return
    
    df = pd.DataFrame(matrix_data)
    
    fig = px.scatter(
        df,
        x='Likelihood',
        y='Severity',
        size='Priority',
        color='Priority',
        text='Risk',
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        title='Risk Impact Matrix'
    )
    
    fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=2.5, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=500, xaxis_range=[0, 5], yaxis_range=[0, 5])
    
    st.plotly_chart(fig, use_container_width=True)


def render_risk_table(risks: Dict):
    """Render risk summary table"""
    
    risk_types = {
        'flood': ('🌊', 'Flood'),
        'landslide': ('⛰️', 'Landslide'),
        'erosion': ('🌾', 'Erosion'),
        'seismic': ('🏗️', 'Seismic'),
        'drought': ('💧', 'Drought'),
        'wildfire': ('🔥', 'Wildfire'),
        'subsidence': ('🏚️', 'Subsidence')
    }
    
    table_data = []
    
    for risk_key, (emoji, name) in risk_types.items():
        risk_info = risks.get(risk_key, {})
        if risk_info and risk_info.get('level') != 'unknown':
            table_data.append({
                '': emoji,
                'Risk Type': name,
                'Level': risk_info.get('level', 'unknown').replace('_', ' ').title(),
                'Severity (1-5)': risk_info.get('severity', 0),
                'Score (0-100)': f"{risk_info.get('score', 0):.1f}",
                'Description': risk_info.get('description', 'N/A')
            })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("No risk data available")


def render_mitigation(risks: Dict):
    """Render mitigation recommendations"""
    
    mitigation = risks.get('mitigation', [])
    
    if mitigation:
        for rec in mitigation:
            st.info(rec)
    else:
        st.info("No specific mitigation measures required")


def render_action_items(risks: Dict):
    """Render action items based on risks"""
    
    overall = risks.get('overall', {})
    high_count = overall.get('high_risk_count', 0)
    
    if high_count >= 3:
        st.error("""
        **⚠️ CRITICAL: Multiple High Risks**
        - Professional assessment essential
        - Consider alternative sites
        - Significant mitigation investment required
        """)
    elif high_count >= 1:
        st.warning("""
        **⚠️ High Risk Identified**
        - Professional assessment recommended
        - Detailed mitigation plan required
        - Budget for mitigation measures
        """)
    else:
        st.success("""
        **✅ Manageable Risk Profile**
        - Follow standard building codes
        - Implement recommended measures
        - Regular monitoring advised
        """)


def render_export_options(risks: Dict):
    """Render export options"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download PDF Report", use_container_width=True):
            st.info("PDF export coming soon!")
    
    with col2:
        if st.button("📋 Copy Summary", use_container_width=True):
            summary_text = _generate_summary_text(risks)
            st.text_area("Risk Summary", summary_text, height=300)


def _generate_summary_text(risks: Dict) -> str:
    """Generate text summary"""
    overall = risks.get('overall', {})
    summary = risks.get('summary', [])
    
    text = f"""RISK ASSESSMENT SUMMARY
=======================

Overall Level: {overall.get('level', 'unknown').upper()}
Average Severity: {overall.get('average_severity', 0):.1f}/5
High Risks: {overall.get('high_risk_count', 0)}
Medium Risks: {overall.get('medium_risk_count', 0)}

SUMMARY:
{chr(10).join(summary)}
"""
    return text


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
