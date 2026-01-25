# utils/ee_manager.py

import ee
import json
import streamlit as st

class EarthEngineManager:
    _available = False

    @classmethod
    def initialize(cls) -> bool:
        try:
            # ✅ Already initialized (Streamlit rerun-safe)
            if ee.data._initialized:
                cls._available = True
                return True

            # ===== Streamlit Cloud =====
            if "GEE_SERVICE_ACCOUNT_JSON" not in st.secrets:
                raise RuntimeError("GEE_SERVICE_ACCOUNT_JSON not found in Streamlit secrets")

            info = json.loads(st.secrets["GEE_SERVICE_ACCOUNT_JSON"])

            credentials = ee.ServiceAccountCredentials(
                info["client_email"],
                key_data=st.secrets["GEE_SERVICE_ACCOUNT_JSON"]
            )

            ee.Initialize(
                credentials=credentials,
                project=st.secrets["GEE_PROJECT_ID"]
            )

            # 🔍 Hard test (forces auth validation)
            ee.Number(1).getInfo()

            cls._available = True
            print("✅ Earth Engine initialized successfully (Streamlit Cloud)")
            return True

        except Exception as e:
            cls._available = False
            print("❌ Earth Engine init failed:", e)
            return False

    @classmethod
    def is_available(cls) -> bool:
        return cls._available

    @classmethod
    def require_ee(cls):
        if not cls._available:
            raise RuntimeError(
                "Earth Engine unavailable.\n"
                "Check Streamlit secrets + service account permissions."
            )
