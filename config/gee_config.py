import os
import ee
import json
import streamlit as st

class GEEConfig:
    """Google Earth Engine Configuration"""

    @classmethod
    def initialize(cls):
        """Initialize Earth Engine (local + Streamlit Cloud safe + interactive fallback)"""

        # ✅ Fast check (no API call)
        if ee.data._initialized:
            return True

        try:
            # ===== Streamlit Cloud =====
            if "GEE_SERVICE_ACCOUNT_JSON" in st.secrets:
                info = json.loads(st.secrets["GEE_SERVICE_ACCOUNT_JSON"])
                credentials = ee.ServiceAccountCredentials(
                    info["client_email"],
                    key_data=st.secrets["GEE_SERVICE_ACCOUNT_JSON"]
                )
                ee.Initialize(credentials, project=st.secrets["GEE_PROJECT_ID"])
                print("✓ EE initialized (Streamlit Cloud)")
                return True

            # ===== Local (.env + service account file) =====
            service_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            project_id = os.getenv("GEE_PROJECT_ID")

            if service_key and os.path.exists(service_key):
                credentials = ee.ServiceAccountCredentials(None, service_key)
                ee.Initialize(credentials, project=project_id)
                print("✓ EE initialized (local service account)")
                return True

            # ===== Fallback: interactive authentication =====
            print("⚠️ No service account found. Attempting interactive authentication...")
            ee.Authenticate()  # opens browser for user login
            ee.Initialize()
            print("✓ EE initialized (interactive user authentication)")
            return True

        except Exception as e:
            raise RuntimeError(
                "✗ Earth Engine initialization failed.\n"
                "• Local: check GOOGLE_APPLICATION_CREDENTIALS\n"
                "• Cloud: check st.secrets\n"
                "• Interactive: browser login required\n\n"
                f"Error: {e}"
            )
