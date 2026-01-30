# ============================================================================
# FILE: ui/components/risk_dashboard.py (IMPROVED VERSION)
# ============================================================================

import streamlit as st
import plotly.graph_objects as go
from typing import Dict

def render_comprehensive_risks(results: Dict):
    """
    Render comprehensive risk assessment dashboard
    Shows all 7 risk types with detailed visualizations
    """
    
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    # IMPROVED ERROR HANDLING
    if not comprehensive_risks or comprehensive_risks.get('overall', {}).get('level') == 'unknown':
        st.warning("""
        ⚠️ **Comprehensive risk assessment not available**
        
        **Why?** The analysis didn't generate risk data.
        
        **Solution:**
        1. Deploy the updated files from the deployment guide
        2. Re-run your land analysis
        3. Risk assessment will then be available
        
        **Files needed:**
        - `data/feature_extraction/fallback_risk_assessment.py` (NEW)
        - `data/feature_extraction/environmental_features.py` (UPDATED)
        """)
        
        with st.expander("📋 Deployment Instructions"):
            st.markdown("""
            ### Quick Fix:
            
            1. **Upload these files to GitHub:**
               - `fallback_risk_assessment.py` → `data/feature_extraction/`
               - `environmental_features_UPDATED.py` → Replace `data/feature_extraction/environmental_features.py`
            
            2. **Commit and push:**
               ```bash
               git add data/feature_extraction/
               git commit -m "Add risk assessment fallback system"
               git push origin main
               ```
            
            3. **Wait 30 seconds** for Streamlit Cloud to redeploy
            
            4. **Run a new analysis** - risk data will be generated!
            
            ### Files Available:
            Check your downloaded outputs for:
            - `RISK_ASSESSMENT_FIX_DEPLOYMENT_GUIDE.md` (complete instructions)
            - `fallback_risk_assessment.py` (new file)
            - `environmental_features_UPDATED.py` (replacement)
            """)
        
        return
    
    # Show data quality indicator
    data_quality = env.get('data_quality', 'unknown')
    
    if data_quality == 'estimated':
        st.info("""
        ℹ️ **Risk Assessment Mode:** Estimation-based (Fallback System Active)
        
        This analysis uses intelligent location and terrain-based estimates since Google Earth Engine 
        is not configured. The system provides reasonable risk assessments based on:
        - Geographic location (latitude/longitude)
        - Terrain features (slope, elevation)
        - Algeria-specific seismic zones
        - Climate patterns
        
        **For higher accuracy:** Configure Google Earth Engine in Streamlit secrets
        (See GEE Configuration Guide)
        """)
    elif data_quality == 'gee':
        st.success("✅ **Risk Assessment Mode:** Earth Engine (High Accuracy) - Using satellite data")
    
    st.markdown("### 🛡️ Comprehensive Risk Assessment")
    
    # Overall risk summary
    overall_risk = comprehensive_risks.get('overall', {})
    risk_summary = comprehensive_risks.get('summary', [])
    
    with st.expander("📊 Overall Risk Profile", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            level = overall_risk.get('level', 'unknown')
            color = _get_risk_color(level)
            st.markdown(f"""
            <div style='background-color:{color};padding:20px;border-radius:10px;text-align:center;'>
                <h2 style='color:white;margin:0;'>{level.replace('_', ' ').title()}</h2>
                <p style='color:white;margin:5px 0 0 0;'>Overall Risk Level</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "Average Severity", 
                f"{overall_risk.get('average_severity', 0):.1f}/5",
                help="Average across all risk types"
            )
        
        with col3:
            high_count = overall_risk.get('high_risk_count', 0)
            medium_count = overall_risk.get('medium_risk_count', 0)
            st.metric(
                "Critical Risks", 
                f"{high_count} High",
                delta=f"{medium_count} Medium" if medium_count > 0 else None
            )
        
        # Summary text
        if risk_summary:
            st.markdown("**Summary:**")
            for line in risk_summary:
                st.markdown(line)
    
    st.markdown("---")
    
    # Individual risk assessments
    st.markdown("### 🔍 Detailed Risk Breakdown")
    
    risk_types = {
        'flood': ('🌊', 'Flood Risk'),
        'landslide': ('⛰️', 'Landslide Risk'),
        'erosion': ('🌾', 'Erosion Risk'),
        'seismic': ('🏗️', 'Seismic Risk'),
        'drought': ('💧', 'Drought Risk'),
        'wildfire': ('🔥', 'Wildfire Risk'),
        'subsidence': ('🏚️', 'Subsidence Risk')
    }
    
    # Create two columns for risk cards
    col1, col2 = st.columns(2)
    
    for idx, (risk_key, (emoji, title)) in enumerate(risk_types.items()):
        risk_data = comprehensive_risks.get(risk_key, {})
        
        if not risk_data or risk_data.get('level') == 'unknown':
            continue
        
        # Alternate between columns
        with col1 if idx % 2 == 0 else col2:
            _render_risk_card(emoji, title, risk_data)
    
    st.markdown("---")
    
    # Risk severity chart
    _render_risk_severity_chart(comprehensive_risks, risk_types)
    
    st.markdown("---")
    
    # Mitigation recommendations
    mitigation = comprehensive_risks.get('mitigation', [])
    if mitigation:
        st.markdown("### 🛠️ Risk Mitigation Recommendations")
        
        for recommendation in mitigation:
            st.info(recommendation)


def _render_risk_card(emoji: str, title: str, risk_data: Dict):
    """Render individual risk assessment card"""
    
    level = risk_data.get('level', 'unknown')
    severity = risk_data.get('severity', 0)
    score = risk_data.get('score', 0)
    description = risk_data.get('description', 'No description')
    factors = risk_data.get('primary_factors', [])
    impact = risk_data.get('impact', 'Unknown impact')
    
    # Color based on severity
    if severity >= 4:
        color = "#d32f2f"  # Red
    elif severity >= 3:
        color = "#f57c00"  # Orange
    elif severity >= 2:
        color = "#fbc02d"  # Yellow
    else:
        color = "#388e3c"  # Green
    
    with st.expander(f"{emoji} **{title}** - {level.replace('_', ' ').title()}", expanded=(severity >= 4)):
        # Severity indicator
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div style='background-color:{color};padding:15px;border-radius:8px;text-align:center;'>
                <h3 style='color:white;margin:0;'>{severity}/5</h3>
                <p style='color:white;margin:5px 0 0 0;font-size:12px;'>Severity</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Progress bar for score
            st.markdown(f"**Risk Score:** {score:.1f}/100")
            st.progress(min(score / 100, 1.0))
        
        # Description
        st.markdown(f"**Description:** {description}")
        
        # Primary factors
        if factors:
            st.markdown("**Key Factors:**")
            for factor in factors:
                st.markdown(f"• {factor}")
        
        # Impact
        st.markdown(f"**Potential Impact:** {impact}")


def _render_risk_severity_chart(risks: Dict, risk_types: Dict):
    """Render horizontal bar chart of risk severities"""
    
    st.markdown("### 📊 Risk Severity Comparison")
    
    risk_names = []
    severities = []
    colors = []
    
    for risk_key, (emoji, title) in risk_types.items():
        risk_data = risks.get(risk_key, {})
        
        if risk_data and risk_data.get('level') != 'unknown':
            risk_names.append(f"{emoji} {title.replace(' Risk', '')}")
            severity = risk_data.get('severity', 0)
            severities.append(severity)
            
            # Color based on severity
            if severity >= 4:
                colors.append('#d32f2f')
            elif severity >= 3:
                colors.append('#f57c00')
            elif severity >= 2:
                colors.append('#fbc02d')
            else:
                colors.append('#388e3c')
    
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
    """Get color for risk level"""
    colors = {
        'very_high': '#d32f2f',
        'high': '#f57c00',
        'medium': '#fbc02d',
        'low': '#388e3c',
        'very_low': '#1b5e20'
    }
    return colors.get(level, '#757575')


def render_risk_summary_metrics(results: Dict):
    """
    Render quick risk summary metrics for the top of results page
    """
    
    features = results.get('features', {})
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    if not comprehensive_risks or comprehensive_risks.get('overall', {}).get('level') == 'unknown':
        return
    
    overall = comprehensive_risks.get('overall', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        flood = comprehensive_risks.get('flood', {})
        st.metric(
            "🌊 Flood",
            flood.get('level', 'Unknown').replace('_', ' ').title(),
            help=flood.get('description', '')
        )
    
    with col2:
        landslide = comprehensive_risks.get('landslide', {})
        st.metric(
            "⛰️ Landslide",
            landslide.get('level', 'Unknown').replace('_', ' ').title(),
            help=landslide.get('description', '')
        )
    
    with col3:
        seismic = comprehensive_risks.get('seismic', {})
        st.metric(
            "🏗️ Seismic",
            seismic.get('level', 'Unknown').replace('_', ' ').title(),
            help=seismic.get('description', '')
        )
    
    with col4:
        st.metric(
            "📊 Overall",
            overall.get('level', 'Unknown').replace('_', ' ').title(),
            delta=f"{overall.get('high_risk_count', 0)} High Risks"
        )
