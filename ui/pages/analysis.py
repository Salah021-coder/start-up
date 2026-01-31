# ============================================================================
# FILE: ui/pages/analysis.py
# ============================================================================

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from core.boundary_manager import BoundaryManager
from core.criteria_engine import CriteriaEngine
from core.analysis_processor import AnalysisProcessor

def render():
    """Render analysis page"""
    
    st.title("🗺️ Land Analysis")
    
    # Boundary input method selection
    st.markdown("### Step 1: Define Your Land Boundary")
    
    method = st.radio(
        "Choose input method:",
        ["Draw on Map", "Upload File", "Use Sample"],
        horizontal=True
    )
    
    if method == "Draw on Map":
        render_interactive_map()
    elif method == "Upload File":
        render_file_upload()
    else:
        render_sample_boundary()

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


def render_interactive_map():
    """Render FULLY INTERACTIVE map with drawing"""
    
    st.info("💡 Use the drawing tools on the left side of the map to draw your boundary")
    
    # Initialize map center (you can make this dynamic based on user location)
    if 'map_center' not in st.session_state:
        st.session_state.map_center = [36.19, 5.41]  # Sétif, Algeria
        st.session_state.map_zoom = 13
    
    # Create Folium map
    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        tiles='OpenStreetMap'
    )
    
    # Add satellite layer option
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add drawing controls
    Draw(
        export=True,
        filename='boundary.geojson',
        position='topleft',
        draw_options={
            'polyline': False,
            'rectangle': True,
            'polygon': True,
            'circle': False,
            'marker': False,
            'circlemarker': False,
        },
        edit_options={'edit': True}
    ).add_to(m)
    
    # Layer control
    folium.LayerControl().add_to(m)
    
    # Display map and capture interactions
    map_data = st_folium(
        m,
        width=800,
        height=500,
        returned_objects=["all_drawings", "last_active_drawing"]
    )
    
    # Process drawn boundaries
    if map_data and map_data.get('all_drawings'):
        drawings = map_data['all_drawings']
        
        if drawings:
            st.success(f"✅ {len(drawings)} boundary(ies) drawn")
            
            # Get the last drawn feature
            last_drawing = drawings[-1]
            
            if last_drawing and 'geometry' in last_drawing:
                # Extract coordinates
                coords = extract_coordinates_from_geojson(last_drawing)
                
                if coords:
                    # Create boundary
                    manager = BoundaryManager()
                    try:
                        boundary_data = manager.create_from_coordinates(coords)
                        st.session_state.boundary_data = boundary_data
                        
                        # Display boundary info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            metric_card("Area", f"{boundary_data['area_hectares']:.2f} ha")
                        with col2:
                            metric_card("Area", f"{boundary_data['area_acres']:.2f} acres")
                        with col3:
                            metric_card("Perimeter", f"{boundary_data['perimeter_m']:.0f} m")
                        
                    except Exception as e:
                        st.error(f"Error creating boundary: {str(e)}")
    
    # Analyze button
    if st.session_state.get('boundary_data'):
        st.markdown("---")
        st.markdown("### Step 2: Start Analysis")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🚀 Analyze This Land", type="primary", use_container_width=True):
                run_analysis()
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.boundary_data = None
                st.rerun()


def extract_coordinates_from_geojson(geojson_feature):
    """Extract coordinates from GeoJSON feature"""
    try:
        geometry = geojson_feature['geometry']
        geom_type = geometry['type']
        
        if geom_type == 'Polygon':
            # Polygon coordinates are [[[lon, lat], [lon, lat], ...]]
            coords = geometry['coordinates'][0]
        elif geom_type == 'Rectangle' or geom_type == 'MultiPolygon':
            # Get first polygon
            coords = geometry['coordinates'][0][0]
        else:
            return None
        
        # Convert to [lon, lat] pairs
        return [[lon, lat] for lon, lat in coords]
        
    except Exception as e:
        st.error(f"Error extracting coordinates: {e}")
        return None


def render_file_upload():
    """Render file upload interface"""
    
    st.markdown("Upload your boundary file:")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['geojson', 'kml', 'json'],
        help="Supported formats: GeoJSON, KML"
    )
    
    if uploaded_file:
        try:
            # Read file content
            import json
            content = uploaded_file.read()
            
            # Try to parse as JSON/GeoJSON
            data = json.loads(content)
            
            # Create boundary manager
            manager = BoundaryManager()
            boundary_data = manager.import_from_geojson_dict(data)
            
            st.session_state.boundary_data = boundary_data
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display on map
            m = folium.Map(
                location=boundary_data['centroid'],
                zoom_start=14
            )
            
            # Add boundary to map
            folium.GeoJson(
                boundary_data['geojson'],
                style_function=lambda x: {
                    'fillColor': 'blue',
                    'color': 'blue',
                    'weight': 2,
                    'fillOpacity': 0.3
                }
            ).add_to(m)
            
            st_folium(m, width=800, height=400)
            
            # Show metrics
            col1, col2 = st.columns(2)
            with col1:
                metric_card("Area", f"{boundary_data['area_hectares']:.2f} ha")
            with col2:
                metric_card("Perimeter", f"{boundary_data['perimeter_m']:.0f} m")
            
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    
    # Analyze button
    if st.session_state.get('boundary_data'):
        st.markdown("---")
        if st.button("🚀 Analyze This Land", type="primary", use_container_width=True):
            run_analysis()


def render_sample_boundary():
    """Quick sample boundary for testing"""
    
    st.info("Use this sample boundary to quickly test the application")
    
    if st.button("Load Sample Boundary", type="primary"):
        # Sample coordinates for a small area
        sample_coords = [
            [5.41, 36.19],
            [5.42, 36.19],
            [5.42, 36.20],
            [5.41, 36.20],
            [5.41, 36.19]
        ]
        
        manager = BoundaryManager()
        boundary_data = manager.create_from_coordinates(sample_coords)
        st.session_state.boundary_data = boundary_data
        
        # Display on map
        m = folium.Map(
            location=boundary_data['centroid'],
            zoom_start=14
        )
        
        folium.GeoJson(
            boundary_data['geojson'],
            style_function=lambda x: {
                'fillColor': 'green',
                'color': 'green',
                'weight': 2,
                'fillOpacity': 0.3
            }
        ).add_to(m)
        
        st_folium(m, width=800, height=400)
        
        st.success("✅ Sample boundary loaded!")
    
    if st.session_state.get('boundary_data'):
        if st.button("🚀 Analyze This Land", type="primary", use_container_width=True):
            run_analysis()


def run_analysis():
    """
    Run the land analysis.

    Flow:
        1. CriteriaEngine picks weights           → {"criteria": {…}, "land_use": "…"}
        2. AnalysisProcessor runs the pipeline    → delegates to AnalysisService
                                                  → converts AnalysisResult to dict internally
        3. Store directly into session_state      → results.py, risk_analysis.py, chatbot
                                                    can all safely call .get() on it
    """
    boundary_data = st.session_state.boundary_data
    
    # Show progress
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    def update_progress(message, percent):
        progress_text.text(message)
        progress_bar.progress(percent / 100)
    
    try:
        # Step 1 – select criteria
        update_progress("Auto-selecting evaluation criteria...", 10)
        criteria_engine = CriteriaEngine()
        criteria_result = criteria_engine.auto_select_criteria(boundary_data)
        # criteria_result == {"criteria": {…nested weights…}, "land_use": "residential"}

        # Step 2 – run pipeline
        # AnalysisProcessor internally:
        #   • calls AnalysisService.analyze_land()
        #   • which calls AnalysisPipeline.run_analysis()
        #   • converts the returned AnalysisResult dataclass via .to_legacy_format()
        # So what comes back is always a plain dict — safe to store directly.
        update_progress("Running comprehensive analysis...", 20)
        processor = AnalysisProcessor()

        results = processor.run_analysis(
            boundary_data,
            criteria_result['criteria'],      # the nested weight dict
            progress_callback=update_progress
        )

        # Step 3 – hand off to results page
        # results is already a plain dict (AnalysisProcessor guarantees this)
        st.session_state.analysis_results = results
        st.session_state.current_page     = 'results'
        
        st.success("✅ Analysis complete!")
        st.balloons()
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        st.info("Please try again or contact support if the problem persists.")
