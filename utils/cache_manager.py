# ============================================================================
# FILE: utils/cache_manager.py
# Cache Management for API Responses
# ============================================================================

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Simple file-based cache for API responses
    
    Helps reduce API calls to Earth Engine and Overpass
    """
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time-to-live for cache entries (hours)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        
        logger.info(f"Cache manager initialized: {self.cache_dir}, TTL: {ttl_hours}h")
    
    def get(self, key: str) -> any:
        """
        Get cached value
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_file = self._get_cache_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            # Check if expired
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - file_time > self.ttl:
                logger.debug(f"Cache expired: {key}")
                cache_file.unlink()
                return None
            
            # Read cache
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            logger.debug(f"Cache hit: {key}")
            return data
            
        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None
    
    def set(self, key: str, value: any):
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        cache_file = self._get_cache_path(key)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(value, f)
            
            logger.debug(f"Cache set: {key}")
            
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")
    
    def delete(self, key: str):
        """Delete cache entry"""
        cache_file = self._get_cache_path(key)
        
        if cache_file.exists():
            cache_file.unlink()
            logger.debug(f"Cache deleted: {key}")
    
    def clear(self):
        """Clear all cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        
        logger.info("Cache cleared")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        # Hash key to create safe filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.json"))
        
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'entries': len(cache_files),
            'size_bytes': total_size,
            'size_mb': round(total_size / (1024 * 1024), 2)
        }
