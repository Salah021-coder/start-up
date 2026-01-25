# ============================================================================
# FILE: utils/ee_manager.py (COMPLETE VERSION)
# ============================================================================

import os
from pathlib import Path

class EarthEngineManager:
    """Manage Google Earth Engine initialization"""
    
    _initialized = False
    _available = False
    
    @classmethod
    def initialize(cls) -> bool:
        """
        Initialize Google Earth Engine
        Returns True if successful, False otherwise
        """
        if cls._initialized:
            return cls._available
        
        try:
            import ee
            
            # Try to initialize
            try:
                # Check if already initialized
                ee.Number(1).getInfo()
                print("✓ Earth Engine already initialized")
                cls._available = True
                cls._initialized = True
                return True
            except:
                pass
            
            # Check for service account credentials
            service_account_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if service_account_key and Path(service_account_key).exists():
                # Use service account
                credentials = ee.ServiceAccountCredentials(
                    email=None,
                    key_file=service_account_key
                )
                project_id = os.getenv('GEE_PROJECT_ID', 'ee-project')
                ee.Initialize(credentials, project=project_id)
                print("✓ Earth Engine initialized with service account")
                cls._available = True
                
            else:
                # Try user authentication
                try:
                    ee.Initialize()
                    print("✓ Earth Engine initialized with user credentials")
                    cls._available = True
                except ee.EEException as e:
                    if 'credentials' in str(e).lower() or 'authenticate' in str(e).lower():
                        print("\n" + "="*60)
                        print("⚠️  EARTH ENGINE NOT AUTHENTICATED")
                        print("="*60)
                        print("\nTo enable Earth Engine, run this command:")
                        print("  earthengine authenticate")
                        print("\nThen restart the application.")
                        print("="*60 + "\n")
                        cls._available = False
                    else:
                        print(f"⚠️ Earth Engine error: {e}")
                        cls._available = False
            
            cls._initialized = True
            return cls._available
            
        except ImportError:
            print("\n" + "="*60)
            print("⚠️  EARTH ENGINE NOT INSTALLED")
            print("="*60)
            print("\nInstall Earth Engine with:")
            print("  pip install earthengine-api")
            print("\nThen authenticate with:")
            print("  earthengine authenticate")
            print("="*60 + "\n")
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
        """Check if Earth Engine is available"""
        if not cls._initialized:
            cls.initialize()
        return cls._available
    
    @classmethod
    def require_ee(cls):
        """Raise error if Earth Engine is not available"""
        if not cls.is_available():
            raise RuntimeError(
                "Google Earth Engine is required for this operation.\n"
                "Please run: earthengine authenticate"
            )