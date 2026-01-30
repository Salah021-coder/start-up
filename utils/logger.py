import logging
import sys
from pathlib import Path

def setup_logger():
    """Setup application logger"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'land_evaluation.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_logger(name: str):
    """Get logger instance"""
    return logging.getLogger(name)

