import streamlit as st
from datetime import datetime

def metric_card(title, value, delta=None):
    delta_html = ""
    if delta is not None:
        color = "#22c55e" if delta.startswith("+") else "#ef4444"
        delta_html = f"""
        <div style="margin-top:6px;font-size:14px;color:{color};font-weight:600;">
            {delta}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            background:#020617;
            border:1px solid #1e293b;
            border-radius:14px;
            padding:18px;
            height:120px;
        ">
            <div style="color:#94a3b8;font-size:13px;">{title}</div>
            <div style="color:white;font-size:34px;font-weight:700;margin-top:6px;">
                {value}
            </div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render():
    """Render analysis history page"""
    
    st.title("📜 Analysis History")
    
    st.info("💡 Your analysis history will be saved here for future reference")
    
    # Mock history data
    if st.session_state.get('analysis_results'):
        st.markdown("### Recent Analyses")
        
        result = st.session_state.analysis_results
        
        with st.expander(f"Analysis - {result.get('analysis_id')}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                metric_card("Score", f"{result.get('overall_score', 0):.1f}/10")
            
            with col2:
                area = result.get('boundary', {}).get('area_hectares', 0)
                metric_card("Area", f"{area:.2f} ha")
            
            with col3:
                metric_card("Date", datetime.now().strftime("%Y-%m-%d"))
            
            if st.button("View Full Results", key="view_history_1"):
                st.session_state.current_page = 'results'
                st.rerun()
    else:
        st.markdown("No analyses yet. Start your first analysis!")
        if st.button("Start New Analysis"):
            st.session_state.current_page = 'analysis'
            st.rerun()

