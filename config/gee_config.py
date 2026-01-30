# ============================================================================
# FILE: config/gee_config.py (ENHANCED WITH ADDITIONAL DATASETS)
# Google Earth Engine Configuration with Comprehensive Dataset Collection
# ============================================================================

import os
import ee
import json
from pathlib import Path

class GEEConfig:
    """Enhanced Google Earth Engine Configuration with 30+ datasets"""

    # Authentication
    SERVICE_ACCOUNT_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    PROJECT_ID = os.getenv("GEE_PROJECT_ID", "mechakra-2003")

    # Comprehensive Dataset Collection
    DATASETS = {
        # ========== ELEVATION & TERRAIN ==========
        "elevation": {
            "srtm": "USGS/SRTMGL1_003",  # 30m resolution
            "aster": "ASTER/GDEM/V3",  # 30m resolution
            "alos": "JAXA/ALOS/AW3D30/V3_2",  # 30m resolution - High quality
            "nasadem": "NASA/NASADEM_HGT/001",  # 30m - Latest NASA DEM
            "etopo1": "NOAA/NGDC/ETOPO1",  # Global bathymetry and topography
        },
        
        # ========== LAND COVER & CLASSIFICATION ==========
        "land_cover": {
            "esa_worldcover": "ESA/WorldCover/v200",  # 10m - 2021 data
            "modis": "MODIS/006/MCD12Q1",  # 500m - Annual land cover
            "copernicus": "COPERNICUS/Landcover/100m/Proba-V-C3/Global",  # 100m
            "dynamic_world": "GOOGLE/DYNAMICWORLD/V1",  # 10m - Near real-time
            "globcover": "ESA/GLOBCOVER_L4_200901_200912_V2_3",  # 300m
        },
        
        # ========== VEGETATION & AGRICULTURE ==========
        "vegetation": {
            "sentinel2": "COPERNICUS/S2_SR_HARMONIZED",  # 10m - High resolution
            "landsat8": "LANDSAT/LC08/C02/T1_L2",  # 30m
            "landsat9": "LANDSAT/LC09/C02/T1_L2",  # 30m
            "modis_ndvi": "MODIS/061/MOD13Q1",  # 250m - 16-day NDVI
            "modis_evi": "MODIS/061/MOD13A1",  # 500m - Enhanced Vegetation Index
            "sentinel1": "COPERNICUS/S1_GRD",  # Radar - works through clouds
        },
        
        # ========== SOIL PROPERTIES ==========
        "soil": {
            # Soil texture (sand, silt, clay content)
            "texture": "OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02",
            "sand_content": "OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02",
            "clay_content": "OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02",
            "silt_content": "OpenLandMap/SOL/SOL_SILT-WFRACTION_USDA-3A1A1A_M/v02",
            
            # Soil properties
            "organic_carbon": "OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02",
            "ph": "OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02",
            "bulk_density": "OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02",
            
            # Soil water
            "water_content": "OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01",
            
            # ISRIC SoilGrids
            "soilgrids_organic": "ISRIC/SoilGrids/v2017-03-10/mean/organic_carbon",
            "soilgrids_ph": "ISRIC/SoilGrids/v2017-03-10/mean/ph",
        },
        
        # ========== WATER RESOURCES ==========
        "water": {
            # Surface water
            "jrc_water": "JRC/GSW1_4/GlobalSurfaceWater",  # Water occurrence
            "jrc_monthly": "JRC/GSW1_4/MonthlyHistory",  # Monthly water history
            
            # Precipitation
            "chirps": "UCSB-CHG/CHIRPS/DAILY",  # Daily rainfall
            "gpm": "NASA/GPM_L3/IMERG_V06",  # 30-min precipitation
            "era5_precip": "ECMWF/ERA5_LAND/DAILY_AGGR",  # Reanalysis precipitation
            
            # Evapotranspiration
            "modis_et": "MODIS/006/MOD16A2",  # 8-day ET
            
            # Groundwater
            "grace": "NASA/GRACE/MASS_GRIDS/MASCON_CRI",  # Groundwater changes
        },
        
        # ========== CLIMATE DATA ==========
        "climate": {
            # Temperature
            "era5_temp": "ECMWF/ERA5_LAND/DAILY_AGGR",  # Daily temperature
            "modis_lst": "MODIS/061/MOD11A1",  # Land surface temperature
            "daymet": "NASA/ORNL/DAYMET_V4",  # North America only
            
            # Weather
            "era5_wind": "ECMWF/ERA5_LAND/DAILY_AGGR",  # Wind speed
            "solar_radiation": "ECMWF/ERA5_LAND/DAILY_AGGR",  # Solar radiation
        },
        
        # ========== ROADS & INFRASTRUCTURE ==========
        "infrastructure": {
            "roads": "TIGER/2016/Roads",  # US roads (if applicable)
            "nightlights": "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG",  # Urban development
            "ghsl_built": "JRC/GHSL/P2016/BUILT_LDSMT_GLOBE_V1",  # Built-up areas
            "ghsl_population": "JRC/GHSL/P2016/POP_GPW_GLOBE_V1",  # Population density
            "worldpop": "WorldPop/GP/100m/pop",  # High-res population
        },
        
        # ========== NATURAL HAZARDS ==========
        "hazards": {
            # Flood
            "flood_susceptibility": "JRC/GHSL/P2023A/GHS_FLOOD_PRONE",
            
            # Fire
            "fire_monthly": "FIRMS",  # Active fires
            "burned_area": "MODIS/061/MCD64A1",  # Burned area
            
            # Landslide susceptibility (calculated from slope/geology)
            # Earthquake zones (would need custom dataset)
        },
        
        # ========== ENVIRONMENTAL QUALITY ==========
        "environmental": {
            # Air quality
            "no2": "COPERNICUS/S5P/OFFL/L3_NO2",  # Nitrogen dioxide
            "so2": "COPERNICUS/S5P/OFFL/L3_SO2",  # Sulfur dioxide
            "co": "COPERNICUS/S5P/OFFL/L3_CO",  # Carbon monoxide
            "aerosol": "COPERNICUS/S5P/OFFL/L3_AER_AI",  # Aerosol index
            
            # Forest/biodiversity
            "tree_cover": "UMD/hansen/global_forest_change_2022_v1_10",  # Forest change
            "biodiversity": "RESOLVE/ECOREGIONS/2017",  # Ecoregions
        },
        
        # ========== PROTECTED AREAS & ZONING ==========
        "protected": {
            "protected_areas": "WCMC/WDPA/current/polygons",  # World protected areas
        }
    }

    # Processing parameters
    SCALE = 30  # meters per pixel
    MAX_PIXELS = 1e8

    # Date ranges for analysis
    DEFAULT_DATE_RANGE = {
        "start": "2023-01-01",
        "end": "2023-12-31"
    }
    
    # Historical comparison range (for trends)
    HISTORICAL_DATE_RANGE = {
        "start": "2020-01-01",
        "end": "2020-12-31"
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
                if hasattr(st, "secrets") and "gee" in st.secrets:
                    print("Attempting Earth Engine init with Streamlit secrets...")
                    service_account_info = st.secrets["gee"]["service_account"]
                    project_id = st.secrets["gee"].get("project_id", cls.PROJECT_ID)

                    if isinstance(service_account_info, str):
                        service_account_info = json.loads(service_account_info)

                    credentials = ee.ServiceAccountCredentials(
                        email=service_account_info["client_email"],
                        key_data=service_account_info["private_key"]
                    )

                    ee.Initialize(credentials, project=project_id)
                    print("✓ Earth Engine initialized with Streamlit Cloud secrets")
                    return True
            except ImportError:
                pass
            except Exception as e:
                print(f"Streamlit secrets method failed: {e}")

            # === LOCAL: Try service account file ===
            if cls.SERVICE_ACCOUNT_KEY and Path(cls.SERVICE_ACCOUNT_KEY).exists():
                credentials = ee.ServiceAccountCredentials(
                    email=None,
                    key_file=cls.SERVICE_ACCOUNT_KEY
                )
                ee.Initialize(credentials, project=cls.PROJECT_ID)
                print("✓ Earth Engine initialized with service account file")
                return True

            # === LOCAL: Try user authentication ===
            try:
                ee.Initialize(project=cls.PROJECT_ID)
                print("✓ Earth Engine initialized with user credentials")
                return True
            except ee.EEException as e:
                if "credentials" in str(e).lower():
                    print("❌ Earth Engine not authenticated")
                    print("   Please run: earthengine authenticate")
                    return False
                raise

        except Exception as e:
            print(f"✗ Earth Engine initialization failed: {e}")
            print("\nFor local development, run: earthengine authenticate")
            print("For Streamlit Cloud, add service account to secrets")
            return False

    @classmethod
    def get_dataset(cls, category: str, name: str) -> str:
        """Get dataset ID by category and name"""
        return cls.DATASETS.get(category, {}).get(name, None)

    @classmethod
    def test_connection(cls):
        """Test Earth Engine connectivity"""
        try:
            ee.Number(1).getInfo()
            print("✓ Earth Engine connection OK")
            return True
        except Exception as e:
            print(f"❌ Earth Engine connection failed: {e}")
            return False
    
    @classmethod
    def get_available_datasets(cls, category: str = None) -> dict:
        """Get list of available datasets"""
        if category:
            return cls.DATASETS.get(category, {})
        return cls.DATASETS
    
    @classmethod
    def list_all_datasets(cls):
        """Print all available datasets"""
        print("\n" + "="*70)
        print("AVAILABLE EARTH ENGINE DATASETS")
        print("="*70)
        
        for category, datasets in cls.DATASETS.items():
            print(f"\n{category.upper()}:")
            for name, dataset_id in datasets.items():
                print(f"  • {name}: {dataset_id}")
        
        print("\n" + "="*70)
        print(f"Total: {sum(len(d) for d in cls.DATASETS.values())} datasets")
        print("="*70)
