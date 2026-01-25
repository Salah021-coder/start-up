# ============================================================================
# FILE: utils/ee_manager.py (COMPLETE VERSION)
# ============================================================================

import ee
import json
import streamlit as st

class EarthEngineManager:

    _initialized = False
    _available = False

    @classmethod
    def initialize(cls) -> bool:
        if cls._initialized:
            return cls._available

        try:
            # ===== Streamlit Cloud: service account from secrets =====
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

            cls._available = False
            cls._initialized = True
            return False

        except Exception as e:
            print(f"❌ Earth Engine initialization failed: {e}")
            cls._available = False
            cls._initialized = True
            return False

    @classmethod
    def is_available(cls) -> bool:
        if not cls._initialized:
            cls.initialize()
        return cls._available

    @classmethod
    def require_ee(cls):
        if not cls.is_available():
            raise RuntimeError(
                "Google Earth Engine is required.\n"
                "• Streamlit Cloud: set GEE_SERVICE_ACCOUNT_JSON in st.secrets"
            )
