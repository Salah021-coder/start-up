# ============================================================================
# FILE: config/gee_config.py (COMPLETE WORKING VERSION)
# ============================================================================

import os
import ee
from pathlib import Path

class GEEConfig:
    """Google Earth Engine Configuration"""
    
    # Authentication
    SERVICE_ACCOUNT_KEY = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    PROJECT_ID = os.getenv('GEE_PROJECT_ID', 'ee-project')
    
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
        """Initialize Earth Engine"""
        try:
            # Check if already initialized
            try:
                ee.Number(1).getInfo()
                print("✓ Earth Engine already initialized")
                return True
            except:
                pass
            
            # Try service account first (for production)
            if cls.SERVICE_ACCOUNT_KEY and Path(cls.SERVICE_ACCOUNT_KEY).exists():
                credentials = ee.ServiceAccountCredentials(
                    email=None,
                    key_file=cls.SERVICE_ACCOUNT_KEY
                )
                ee.Initialize(credentials, project=cls.PROJECT_ID)
                print("✓ Earth Engine initialized with service account")
                return True
            
            # Fall back to user authentication
            else:
                # For user authentication, project parameter is optional
                try:
                    ee.Initialize()
                    print("✓ Earth Engine initialized with user credentials")
                    return True
                except ee.EEException as e:
                    if 'credentials' in str(e).lower():
                        print("❌ Earth Engine not authenticated")
                        print("   Please run: earthengine authenticate")
                        return False
                    raise
                
        except Exception as e:
            print(f"✗ Earth Engine initialization failed: {e}")
            print("\nPlease run: earthengine authenticate")
            return False
    
    @classmethod
    def get_dataset(cls, category: str, name: str) -> str:
        """Get dataset ID by category and name"""
        return cls.DATASETS.get(category, {}).get(name)
    
    @classmethod
    def test_connection(cls):
        """Test Earth Engine connection"""
        try:
            # Simple test query
            point = ee.Geometry.Point([0, 0])
            result = ee.Image('USGS/SRTMGL1_003').sample(point, 30).first()
            result.getInfo()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False