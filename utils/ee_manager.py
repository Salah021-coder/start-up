# ============================================================================
# FILE: utils/ee_manager.py
# ============================================================================

import ee
import json
import streamlit as st

class EarthEngineManager:
    """
    Manages Google Earth Engine initialization on Streamlit Cloud.
    Uses a service account from Streamlit secrets.
    """

    _initialized = False
    _available = False

    @classmethod
    def initialize(cls) -> bool:
        """Initialize Earth Engine using service account from Streamlit secrets."""
        if cls._initialized:
            return cls._available

        try:
            # Streamlit Cloud: load service account JSON from secrets
            if "GEE_SERVICE_ACCOUNT_JSON" in st.secrets and "GEE_PROJECT_ID" in st.secrets:
                service_account_info = json.loads(st.secrets["GEE_SERVICE_ACCOUNT_JSON"])
                
                credentials = ee.ServiceAccountCredentials(
                    service_account_info["client_email"],
                    key_data=json.dumps(service_account_info)
                )

                ee.Initialize(credentials, project=st.secrets["GEE_PROJECT_ID"])

                cls._available = True
                cls._initialized = True
                print("✅ Earth Engine initialized successfully (Streamlit Cloud)")
                return True

            else:
                cls._available = False
                cls._initialized = True
                print("❌ Missing GEE_SERVICE_ACCOUNT_JSON or GEE_PROJECT_ID in secrets")
                return False

        except Exception as e:
            cls._available = False
            cls._initialized = True
            print(f"❌ Earth Engine initialization failed: {e}")
            return False

    @classmethod
    def is_available(cls) -> bool:
        """Check if Earth Engine is initialized and available."""
        if not cls._initialized:
            cls.initialize()
        return cls._available

    @classmethod
    def require_ee(cls):
        """Raise error if Earth Engine is not available."""
        if not cls.is_available():
            raise RuntimeError(
                "❌ Google Earth Engine is required.\n"
                "• Make sure your Streamlit Cloud secrets include a valid service account:\n"
                "  GEE_SERVICE_ACCOUNT_JSON and GEE_PROJECT_ID\n"
                "• No 'earthengine authenticate' is needed on Streamlit Cloud."
            )
