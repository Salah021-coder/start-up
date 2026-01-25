# ============================================================================
# FILE: config/gee_config.py (STREAMLIT CLOUD COMPATIBLE)
# ============================================================================

import os
import ee
import json
from pathlib import Path

class GEEConfig:
    """Google Earth Engine Configuration - Works locally and on Streamlit Cloud"""
    
    # Authentication
    SERVICE_ACCOUNT_KEY = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    PROJECT_ID = os.getenv('GEE_PROJECT_ID', 'mechakra-2003')
    
    # Dataset IDs
    DATASETS = {
        'elevation': {
            'srtm': 'USGS/SRTMGL1_003',
            'aster': 'ASTER/GDEM/V3'
        },
        'land_cover': {
            'esa_worldcover': 'ESA/WorldCover/v200',
            'modis': 'MODIS/006/MCD12Q1'
        },
        'vegetation': {
            'sentinel2': 'COPERNICUS/S2_SR_HARMONIZED',
            'landsat8': 'LANDSAT/LC08/C02/T1_L2'
        },
        'soil': {
            'soilgrids': 'OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02'
        },
        'water': {
            'jrc_water': 'JRC/GSW1_4/GlobalSurfaceWater',
            'precipitation': 'UCSB-CHG/CHIRPS/DAILY'
        },
        'climate': {
            'temperature': 'ECMWF/ERA5_LAND/DAILY_AGGR',
            'precipitation': 'UCSB-CHG/CHIRPS/DAILY'
        }
    }
    
    # Processing parameters
    SCALE = 30  # meters per pixel
    MAX_PIXELS = 1e8
    
    # Date ranges for analysis
    DEFAULT_DATE_RANGE = {
        'start': '2023-01-01',
        'end': '2023-12-31'
    }
    
    @classmethod
    def initialize(cls):
        """Initialize Earth Engine - Works on Streamlit Cloud and locally"""
        try:
            # Check if already initialized
            try:
                ee.Number(1).getInfo()
                print("✓ Earth Engine already initialized")
                return True
            except:
                pass
            
            # === STREAMLIT CLOUD: Try Streamlit secrets first ===
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'gee' in st.secrets:
                    print("Attempting Earth Engine init with Streamlit secrets...")
                    
                    # Get service account from secrets
                    service_account_info = st.secrets["gee"]["service_account"]
                    project_id = st.secrets["gee"].get("project_id", cls.PROJECT_ID)
                    
                    # Parse JSON if it's a string
                    if isinstance(service_account_info, str):
                        service_account_info = json.loads(service_account_info)
                    
                    # Create credentials from the JSON data
                    credentials = ee.ServiceAccountCredentials(
                        email=service_account_info['client_email'],
                        key_data=service_account_info['private_key']
                    )
                    
