import ee
import os
from pathlib import Path

def setup_earth_engine():
    """Initialize Google Earth Engine"""
    
    print("Setting up Google Earth Engine...")
    
    # Check for service account
    service_account_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GEE_PROJECT_ID')
    
    if service_account_key and Path(service_account_key).exists():
        print(f"Using service account: {service_account_key}")
        credentials = ee.ServiceAccountCredentials(
            email=None,
            key_file=service_account_key
        )
        ee.Initialize(credentials, project=project_id)
        print("✓ Earth Engine initialized with service account")
    else:
        print("No service account found. Attempting default authentication...")
        try:
            ee.Authenticate()
            ee.Initialize(project=project_id)
            print("✓ Earth Engine initialized with default credentials")
        except Exception as e:
            print(f"✗ Failed to initialize Earth Engine: {e}")
            print("\nPlease run: earthengine authenticate")
            return False
    
    # Test connection
    try:
        image = ee.Image('USGS/SRTMGL1_003')
        info = image.getInfo()
        print("✓ Earth Engine connection test successful")
        return True
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    setup_earth_engine()
