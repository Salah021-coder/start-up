# utils/ee_manager.py

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
            # Load service account JSON from Streamlit secrets
            service_account_info = json.loads(
                st.secrets["GEE_SERVICE_ACCOUNT_JSON"]
            )

            credentials = ee.ServiceAccountCredentials(
                service_account_info["client_email"],
                key_data=json.dumps(service_account_info)
            )

            ee.Initialize(
                credentials,
                project=st.secrets["GEE_PROJECT_ID"]
            )

            # Hard test (real EE call)
            ee.Image("CGIAR/SRTM90_V4").getInfo()

            cls._available = True
            cls._initialized = True
            print("✅ Earth Engine initialized successfully (Streamlit Cloud)")
            return True

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
                "Google Earth Engine is not available. "
                "Check Streamlit Secrets configuration."
            )
