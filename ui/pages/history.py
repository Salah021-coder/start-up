import streamlit as st
from datetime import datetime

def metric_card(title, value, delta=None, height=120):
    """Custom metric card with optional delta (change) indicator."""
    # Handle delta color dynamically
    delta_html = ""
    if delta is not None:
        try:
            delta_value = float(str(delta).replace("%", "").replace("+", ""))
            color = "#22c55e" if delta_value >= 0 else "#ef4444"
        except ValueError:
            color = "#94a3b8"  # fallback neutral
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
            height:{height}px;
            display:flex;
            flex-direction:column;
            justify-content:center;
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

# Example usage
def render():
    st.title("📜 Analysis History")
    st.info("💡 Your analysis history will be saved here for future reference")

    history = st.session_state.get("analysis_results", [])

    if history:
        st.markdown("### Recent Analyses")
        for idx, result in enumerate(history):
            analysis_id = result.get("analysis_id", idx)
            with st.expander(f"Analysis - {analysis_id}", expanded=True, key=f"expander_{analysis_id}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    metric_card("Score", f"{result.get('overall_score', 0):.1f}/10", delta=result.get("score_delta"))

                with col2:
                    area = result.get("boundary", {}).get("area_hectares", 0)
                    metric_card("Area", f"{area:.2f} ha")

                with col3:
                    date = result.get("date", datetime.now().strftime("%Y-%m-%d"))
                    metric_card("Date", date)

                if st.button("View Full Results", key=f"view_{analysis_id}"):
                    st.session_state.current_page = "results"
                    st.session_state.current_analysis = analysis_id
                    st.rerun()
    else:
        st.markdown("No analyses yet. Start your first analysis!")
        if st.button("Start New Analysis"):
            st.session_state.current_page = "analysis"
            st.rerun()


