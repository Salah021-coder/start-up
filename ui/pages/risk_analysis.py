# ============================================================================
# FILE: ui/pages/risk_analysis.py (NEW FILE - DEDICATED RISK ASSESSMENT PAGE)
# ============================================================================

import streamlit as st
from ui.components.risk_dashboard import render_comprehensive_risks, render_risk_summary_metrics
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

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
    
    # Check if comprehensive risk data is available
    if not comprehensive_risks:
        st.error("❌ Comprehensive risk assessment data not available")
        st.info("""
        **Why?** Risk assessment requires Google Earth Engine to be properly configured.
        
        **What to do:**
        1. Ensure GEE is configured in Streamlit secrets
        2. Re-run your land analysis
        3. The system will then perform comprehensive risk assessment
        """)
        return
    
    # Page header with summary
    st.markdown("""
    This page provides a detailed assessment of **7 major risk types** that could affect 
    your land development project. Each risk is evaluated based on real geographic data 
    and terrain analysis.
    """)
    
    st.markdown("---")
    
    # Quick summary metrics
    st.markdown("### 📊 Quick Risk Overview")
    render_risk_summary_metrics(results)
    
    st.markdown("---")
    
    # Full comprehensive risk dashboard
    render_comprehensive_risks(results)
    
    st.markdown("---")
    
    # Risk comparison section
    st.markdown("### 📈 Risk Severity Analysis")
    render_risk_severity_comparison(comprehensive_risks)
    
    st.markdown("---")
    
    # Risk matrix
    st.markdown("### 🎯 Risk Impact Matrix")
    render_risk_matrix(comprehensive_risks)
    
    st.markdown("---")
    
    # Detailed risk breakdown table
    st.markdown("### 📋 Detailed Risk Summary Table")
    render_risk_table(comprehensive_risks)
    
    st.markdown("---")
    
    # Action items
    st.markdown("### ✅ Recommended Actions")
    render_action_items(comprehensive_risks)
    
    st.markdown("---")
    
    # Export options
    st.markdown("### 💾 Export Risk Report")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download PDF Report", use_container_width=True):
            st.info("PDF export feature coming soon!")
    
    with col2:
        if st.button("📊 Export to Excel", use_container_width=True):
            export_to_excel(comprehensive_risks)
    
    with col3:
        if st.button("📋 Copy Summary", use_container_width=True):
            copy_to_clipboard(comprehensive_risks)


def render_risk_severity_comparison(risks: dict):
    """Render detailed risk severity comparison chart"""
    
    risk_types = {
        'flood': ('🌊', 'Flood'),
        'landslide': ('⛰️', 'Landslide'),
        'erosion': ('🌾', 'Erosion'),
        'seismic': ('🏗️', 'Seismic'),
        'drought': ('💧', 'Drought'),
        'wildfire': ('🔥', 'Wildfire'),
        'subsidence': ('🏚️', 'Subsidence')
    }
    
    # Prepare data
    risk_data = []
    for risk_key, (emoji, name) in risk_types.items():
        risk_info = risks.get(risk_key, {})
        if risk_info and risk_info.get('level') != 'unknown':
            risk_data.append({
                'Risk Type': f"{emoji} {name}",
                'Severity': risk_info.get('severity', 0),
                'Score': risk_info.get('score', 0),
                'Level': risk_info.get('level', 'unknown').replace('_', ' ').title()
            })
    
    if not risk_data:
        st.info("No risk data available for comparison")
        return
    
    df = pd.DataFrame(risk_data)
    
    # Create dual-axis chart
    fig = go.Figure()
    
    # Severity bars
    fig.add_trace(go.Bar(
        name='Severity (1-5)',
        x=df['Risk Type'],
        y=df['Severity'],
        marker_color=['#d32f2f' if s >= 4 else '#f57c00' if s >= 3 else '#fbc02d' if s >= 2 else '#388e3c' 
                      for s in df['Severity']],
        text=df['Severity'],
        textposition='auto',
    ))
    
    # Score line
    fig.add_trace(go.Scatter(
        name='Risk Score (0-100)',
        x=df['Risk Type'],
        y=df['Score'],
        mode='lines+markers',
        marker=dict(size=10, color='blue'),
        line=dict(width=3, color='blue'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Risk Severity vs Score Comparison',
        xaxis_title='Risk Type',
        yaxis=dict(
            title='Severity Level (1-5)',
            range=[0, 5]
        ),
        yaxis2=dict(
            title='Risk Score (0-100)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_risk_matrix(risks: dict):
    """Render risk impact/probability matrix"""
    
    st.markdown("""
    This matrix shows where each risk falls in terms of **severity** (impact) and 
    **likelihood** based on the site characteristics.
    """)
    
    risk_types = {
        'flood': '🌊 Flood',
        'landslide': '⛰️ Landslide',
        'erosion': '🌾 Erosion',
        'seismic': '🏗️ Seismic',
        'drought': '💧 Drought',
        'wildfire': '🔥 Wildfire',
        'subsidence': '🏚️ Subsidence'
    }
    
    # Create matrix data
    matrix_data = []
    for risk_key, label in risk_types.items():
        risk_info = risks.get(risk_key, {})
        if risk_info and risk_info.get('level') != 'unknown':
            severity = risk_info.get('severity', 0)
            score = risk_info.get('score', 0)
            
            # Convert score to likelihood (0-5)
            likelihood = score / 20  # 0-100 -> 0-5
            
            matrix_data.append({
                'Risk': label,
                'Severity': severity,
                'Likelihood': likelihood,
                'Priority': severity * likelihood  # Combined priority score
            })
    
    if not matrix_data:
        st.info("No risk data available for matrix")
        return
    
    df = pd.DataFrame(matrix_data)
    
    # Create scatter plot matrix
    fig = px.scatter(
        df,
        x='Likelihood',
        y='Severity',
        size='Priority',
        color='Priority',
        text='Risk',
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        title='Risk Impact Matrix',
        labels={
            'Likelihood': 'Likelihood / Probability (0-5)',
            'Severity': 'Impact / Severity (1-5)'
        }
    )
    
    # Add quadrant lines
    fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=2.5, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=1.2, y=4, text="High Impact<br>Low Likelihood", showarrow=False, opacity=0.5)
    fig.add_annotation(x=3.8, y=4, text="High Impact<br>High Likelihood<br>(CRITICAL)", showarrow=False, opacity=0.7, bgcolor="rgba(255,0,0,0.2)")
    fig.add_annotation(x=1.2, y=1, text="Low Impact<br>Low Likelihood", showarrow=False, opacity=0.5)
    fig.add_annotation(x=3.8, y=1, text="Low Impact<br>High Likelihood", showarrow=False, opacity=0.5)
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=600)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **How to read this matrix:**
    - 🔴 **Top Right (Critical)**: High severity + High likelihood = Immediate action required
    - 🟡 **Other quadrants**: Various priority levels
    - 🟢 **Bottom Left**: Low priority - monitor only
    """)


def render_risk_table(risks: dict):
    """Render detailed risk information in table format"""
    
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
                'Description': risk_info.get('description', 'N/A'),
                'Impact': risk_info.get('impact', 'N/A')
            })
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        # Style the dataframe
        def color_severity(val):
            if val >= 4:
                return 'background-color: #ffcdd2; color: #b71c1c'
            elif val >= 3:
                return 'background-color: #ffe0b2; color: #e65100'
            elif val >= 2:
                return 'background-color: #fff9c4; color: #f57f17'
            else:
                return 'background-color: #c8e6c9; color: #1b5e20'
        
        styled_df = df.style.applymap(color_severity, subset=['Severity (1-5)'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info("No risk data available")


def render_action_items(risks: dict):
    """Render prioritized action items based on risk assessment"""
    
    overall = risks.get('overall', {})
    high_risk_count = overall.get('high_risk_count', 0)
    
    st.markdown(f"""
    Based on the comprehensive risk assessment, here are the **recommended actions** 
    prioritized by urgency and impact.
    
    **Overall Risk Level:** {overall.get('level', 'unknown').replace('_', ' ').title()}  
    **High Priority Risks:** {high_risk_count}
    """)
    
    # Get mitigation recommendations
    mitigation = risks.get('mitigation', [])
    
    if mitigation:
        st.markdown("### 🔧 Priority Mitigation Measures:")
        
        for i, rec in enumerate(mitigation, 1):
            # Determine priority based on content
            if "HIGH" in rec.upper() or "CRITICAL" in rec.upper() or "SEVERE" in rec.upper():
                st.error(f"**{i}. CRITICAL:** {rec}")
            elif "MEDIUM" in rec.upper() or "MODERATE" in rec.upper():
                st.warning(f"**{i}. Important:** {rec}")
            else:
                st.info(f"**{i}.** {rec}")
    
    # Additional recommendations
    st.markdown("### 📝 General Recommendations:")
    
    if high_risk_count >= 3:
        st.error("""
        **⚠️ CRITICAL: Multiple High Risks Detected**
        
        - Strongly recommend comprehensive professional assessment
        - Consider alternative sites if risks cannot be mitigated
        - Budget significant resources for risk mitigation
        - Consult with specialized engineers for each high-risk area
        """)
    elif high_risk_count >= 1:
        st.warning("""
        **⚠️ High Risk Area Identified**
        
        - Professional assessment recommended for high-risk factors
        - Develop detailed mitigation plan before proceeding
        - Include risk mitigation costs in project budget
        - Consider phased development approach
        """)
    else:
        st.success("""
        **✅ Manageable Risk Profile**
        
        - Follow standard building codes and practices
        - Implement recommended mitigation measures
        - Monitor conditions during development
        - Maintain regular inspections and maintenance
        """)


def export_to_excel(risks: dict):
    """Export risk assessment to Excel format"""
    
    import io
    
    # Create summary data
    risk_types = {
        'flood': '🌊 Flood',
        'landslide': '⛰️ Landslide',
        'erosion': '🌾 Erosion',
        'seismic': '🏗️ Seismic',
        'drought': '💧 Drought',
        'wildfire': '🔥 Wildfire',
        'subsidence': '🏚️ Subsidence'
    }
    
    export_data = []
    for risk_key, label in risk_types.items():
        risk_info = risks.get(risk_key, {})
        if risk_info and risk_info.get('level') != 'unknown':
            export_data.append({
                'Risk Type': label,
                'Level': risk_info.get('level', 'unknown').replace('_', ' ').title(),
                'Severity (1-5)': risk_info.get('severity', 0),
                'Score (0-100)': risk_info.get('score', 0),
                'Description': risk_info.get('description', ''),
                'Primary Factors': ', '.join(risk_info.get('primary_factors', [])),
                'Impact': risk_info.get('impact', '')
            })
    
    if export_data:
        df = pd.DataFrame(export_data)
        
        # Convert to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Risk Assessment', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 Download Excel Report",
            data=output,
            file_name="risk_assessment_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No data available to export")


def copy_to_clipboard(risks: dict):
    """Generate text summary for clipboard"""
    
    overall = risks.get('overall', {})
    summary = risks.get('summary', [])
    
    text = f"""
COMPREHENSIVE RISK ASSESSMENT SUMMARY
=====================================

Overall Risk Level: {overall.get('level', 'unknown').replace('_', ' ').upper()}
Average Severity: {overall.get('average_severity', 0):.1f}/5
High Risk Count: {overall.get('high_risk_count', 0)}
Medium Risk Count: {overall.get('medium_risk_count', 0)}

SUMMARY:
{chr(10).join(summary)}

DETAILED RISKS:
"""
    
    risk_types = ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']
    
    for risk_type in risk_types:
        risk_info = risks.get(risk_type, {})
        if risk_info and risk_info.get('level') != 'unknown':
            text += f"""
{risk_type.upper()}:
  Level: {risk_info.get('level', 'unknown').replace('_', ' ').title()}
  Severity: {risk_info.get('severity', 0)}/5
  Score: {risk_info.get('score', 0):.1f}/100
  Description: {risk_info.get('description', 'N/A')}
"""
    
    st.text_area("Risk Assessment Summary (Copy this text)", text, height=400)
    st.info("✅ Copy the text above to share or save the risk assessment summary")
