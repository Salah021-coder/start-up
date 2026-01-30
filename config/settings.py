import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

class Settings:
    """Application-wide settings"""
    
    # Application
    APP_NAME = "Land Evaluation AI"
    VERSION = "1.0.0"
    DEBUG = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paths
    BASE_DIR = PROJECT_ROOT
    CONFIG_DIR = PROJECT_ROOT / 'config'
    DATA_DIR = PROJECT_ROOT / 'data'
    CACHE_DIR = PROJECT_ROOT / 'cache'
    ASSETS_DIR = PROJECT_ROOT / 'assets'
    MODELS_DIR = PROJECT_ROOT / 'intelligence' / 'ml' / 'pretrained'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///land_evaluation.db')
    
    # Cache
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TTL = 3600  # 1 hour
    
    # Analysis Limits
    MAX_ANALYSIS_AREA_KM2 = float(os.getenv('MAX_ANALYSIS_AREA_KM2', '100'))
    MIN_ANALYSIS_AREA_M2 = 100  # 100 square meters
    
    # API Rate Limits
    GEE_MAX_REQUESTS_PER_MINUTE = int(os.getenv('GEE_MAX_REQUESTS_PER_MINUTE', '60'))
    GEMINI_MAX_REQUESTS_PER_MINUTE = int(os.getenv('GEMINI_MAX_REQUESTS_PER_MINUTE', '20'))
    
    @classmethod
    def load_config(cls):
        """Load configuration from YAML file"""
        config_path = cls.CONFIG_DIR / 'config.yaml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.CACHE_DIR, cls.MODELS_DIR, cls.DATA_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
