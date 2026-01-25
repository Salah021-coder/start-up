# ============================================================================
# FILE: utils/ee_manager.py (PRODUCTION-READY VERSION)
# ============================================================================

import os
import json
from pathlib import Path
import streamlit as st

class EarthEngineManager:
    """Manage Google Earth Engine initialization (local + Streamlit Cloud safe)"""
    
    _initialized = False
    _available = False
    
    @classmethod
    def initialize(cls) -> bool:
        """Initialize Google Earth Engine"""
        if cls._initialized:
            return cls._available
        
        try:
            import ee
            
            # ===== Fast check for existing EE session =====
            if ee.data._initialized:
                cls._available = True
                cls._initialized = True
                print("✓ Earth Engine already initialized")
                return True
            
            # ===== Streamlit Cloud: use service account JSON from st.secrets =====
            if "GEE_SERVICE_ACCOUNT_JSON" in st.secrets:
                info = json.loads(st.secrets["GEE_SERVICE_ACCOUNT_JSON"])
                credentials = ee.ServiceAccountCredentials(
                    info["client_email"],
                    key_data=st.secrets["GEE_SERVICE_ACCOUNT_JSON"]
                )
                ee.Initialize(credentials, project=st.secrets["GEE_PROJECT_ID"])
                cls._available = True
                cls._initialized = True
                print("✓ Earth Engine initialized (Streamlit Cloud)")
                return True
            
            # ===== Local: service account file =====
            service_account_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            project_id = os.getenv('GEE_PROJECT_ID', 'ee-project')
            
            if service_account_key and Path(service_account_key).exists():
                credentials = ee.ServiceAccountCredentials(None, key_file=service_account_key)
                ee.Initialize(credentials, project=project_id)
                cls._available = True
                cls._initialized = True
                print("✓ Earth Engine initialized (local service account)")
                return True
            
            # ===== Local fallback: interactive authentication =====
            print("⚠️ No service account found. Attempting interactive login...")
            ee.Authenticate()
            ee.Initialize()
            cls._available = True
            cls._initialized = True
            print("✓ Earth Engine initialized (interactive user authentication)")
            return True
            
        except ImportError:
            print("⚠️ Earth Engine API not installed. Install with: pip install earthengine-api")
            cls._available = False
            cls._initialized = True
            return False
        
        except Exception as e:
            print(f"⚠️ Earth Engine initialization failed: {e}")
            cls._available = False
            cls._initialized = True
            return False
    
    @classmethod
    def is_available(cls) -> bool:
        """Return True if EE is available"""
        if not cls._initialized:
            cls.initialize()
        return cls._available
    
    @classmethod
    def require_ee(cls):
        """Raise exception if EE not available"""
        if not cls.is_available():
            raise RuntimeError(
                "Google Earth Engine is required.\n"
                "• Local: run `earthengine authenticate` or set GOOGLE_APPLICATION_CREDENTIALS\n"
                "• Streamlit Cloud: set GEE_SERVICE_ACCOUNT_JSON in st.secrets"
            )
