"""
Cache Manager for Licensing Analysis
Based on the existing invoice project cache manager but optimized for licensing data
"""

import os
import json
import hashlib
import time
import shutil
import gzip
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from config import CACHE_CONFIG

logger = logging.getLogger(__name__)

class LicensingCacheManager:
    """
    Intelligent cache manager for licensing analysis with TTL, size limits, and automatic cleanup.
    Optimized for licensing data patterns and longer retention periods.
    """
    
    def __init__(self, cache_dir: str = None, max_size_mb: int = None, ttl_days: int = None):
        self.cache_dir = cache_dir or CACHE_CONFIG["cache_dir"]
        self.max_size_bytes = (max_size_mb or CACHE_CONFIG["max_size_mb"]) * 1024 * 1024
        self.ttl_seconds = (ttl_days or CACHE_CONFIG["ttl_days"]) * 24 * 60 * 60
        self.enable_compression = CACHE_CONFIG["enable_compression"]
        self.metadata_file = os.path.join(self.cache_dir, "licensing_cache_metadata.json")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load or initialize metadata
        self.metadata = self._load_metadata()
        
        # Perform cleanup on initialization
        self.cleanup_expired()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from file."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load cache metadata: {e}")
        return {
            "entries": {},
            "total_size": 0,
            "created": datetime.now().isoformat(),
            "last_cleanup": datetime.now().isoformat(),
            "stats": {
                "hits": 0,
                "misses": 0,
                "evictions": 0
            }
        }
    
    def _save_metadata(self):
        """Save cache metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save cache metadata: {e}")
    
    def _get_cache_key(self, identifier: str, content_hash: Optional[str] = None) -> str:
        """Generate a cache key for licensing data."""
        if content_hash:
            return f"licensing_{identifier}_{content_hash[:16]}"
        else:
            return f"licensing_{identifier}_{int(time.time())}"
    
    def _get_content_hash(self, data: Any) -> str:
        """Generate hash of data content."""
        try:
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash data: {e}")
            return ""
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data if compression is enabled."""
        if self.enable_compression:
            data_str = json.dumps(data)
            return gzip.compress(data_str.encode())
        else:
            return json.dumps(data).encode()
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data if compression is enabled."""
        if self.enable_compression:
            data_str = gzip.decompress(compressed_data).decode()
            return json.loads(data_str)
        else:
            return json.loads(compressed_data.decode())
    
    def get(self, identifier: str, data: Any = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached licensing analysis data."""
        content_hash = self._get_content_hash(data) if data else ""
        cache_key = self._get_cache_key(identifier, content_hash)
        
        # Check if entry exists and is valid
        if cache_key not in self.metadata["entries"]:
            self.metadata["stats"]["misses"] += 1
            return None
        
        entry = self.metadata["entries"][cache_key]
        
        # Check if expired
        if time.time() - entry["created"] > self.ttl_seconds:
            logger.info(f"Cache entry expired for {identifier}")
            self._remove_entry(cache_key)
            self.metadata["stats"]["misses"] += 1
            return None
        
        # Check if content has changed (hash mismatch)
        if data and entry.get("content_hash") != content_hash:
            logger.info(f"Content changed for {identifier}")
            self._remove_entry(cache_key)
            self.metadata["stats"]["misses"] += 1
            return None
        
        # Load cached data
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.cache")
        if not os.path.exists(cache_file):
            logger.warning(f"Cache file missing for {identifier}")
            self._remove_entry(cache_key)
            self.metadata["stats"]["misses"] += 1
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                compressed_data = f.read()
                cached_data = self._decompress_data(compressed_data)
            
            # Update access time
            entry["last_accessed"] = time.time()
            self.metadata["stats"]["hits"] += 1
            self._save_metadata()
            
            return cached_data
        except Exception as e:
            logger.error(f"Error loading cached data for {identifier}: {e}")
            self._remove_entry(cache_key)
            self.metadata["stats"]["misses"] += 1
            return None
    
    def set(self, identifier: str, data: Dict[str, Any], data_for_hash: Any = None) -> bool:
        """Store licensing analysis data in cache."""
        content_hash = self._get_content_hash(data_for_hash or data)
        cache_key = self._get_cache_key(identifier, content_hash)
        
        # Compress data
        compressed_data = self._compress_data(data)
        data_size = len(compressed_data)
        
        # Check if we need to evict entries to make space
        if self.metadata["total_size"] + data_size > self.max_size_bytes:
            self._evict_oldest(data_size)
        
        # Create cache entry
        entry = {
            "identifier": identifier,
            "content_hash": content_hash,
            "size": data_size,
            "created": time.time(),
            "last_accessed": time.time(),
            "compressed": self.enable_compression
        }
        
        # Save data to file
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.cache")
        try:
            with open(cache_file, 'wb') as f:
                f.write(compressed_data)
            
            # Update metadata
            self.metadata["entries"][cache_key] = entry
            self.metadata["total_size"] += data_size
            self._save_metadata()
            
            logger.info(f"Cached licensing analysis for {identifier} ({data_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"Error saving cache for {identifier}: {e}")
            return False
    
    def _remove_entry(self, cache_key: str):
        """Remove a cache entry."""
        if cache_key in self.metadata["entries"]:
            entry = self.metadata["entries"][cache_key]
            self.metadata["total_size"] -= entry["size"]
            
            # Remove cache file
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.cache")
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except Exception as e:
                    logger.warning(f"Could not remove cache file {cache_file}: {e}")
            
            del self.metadata["entries"][cache_key]
            self.metadata["stats"]["evictions"] += 1
    
    def _evict_oldest(self, required_size: int):
        """Evict oldest entries to make space."""
        if CACHE_CONFIG["eviction_policy"] == "lru":
            # Sort by last accessed time
            sorted_entries = sorted(
                self.metadata["entries"].items(),
                key=lambda x: x[1]["last_accessed"]
            )
        else:
            # Default to FIFO (first in, first out)
            sorted_entries = sorted(
                self.metadata["entries"].items(),
                key=lambda x: x[1]["created"]
            )
        
        freed_space = 0
        for cache_key, entry in sorted_entries:
            if freed_space >= required_size:
                break
            
            self._remove_entry(cache_key)
            freed_space += entry["size"]
        
        logger.info(f"Evicted {freed_space} bytes to make space for new cache entry")
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for cache_key, entry in self.metadata["entries"].items():
            if current_time - entry["created"] > self.ttl_seconds:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._remove_entry(cache_key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        self.metadata["last_cleanup"] = datetime.now().isoformat()
        self._save_metadata()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self.metadata["entries"]),
            "total_size_mb": self.metadata["total_size"] / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "hit_rate": self.metadata["stats"]["hits"] / max(1, self.metadata["stats"]["hits"] + self.metadata["stats"]["misses"]),
            "hits": self.metadata["stats"]["hits"],
            "misses": self.metadata["stats"]["misses"],
            "evictions": self.metadata["stats"]["evictions"],
            "created": self.metadata["created"],
            "last_cleanup": self.metadata["last_cleanup"]
        }
    
    def clear(self):
        """Clear all cache entries."""
        # Remove all cache files
        for cache_key in list(self.metadata["entries"].keys()):
            self._remove_entry(cache_key)
        
        # Reset metadata
        self.metadata = {
            "entries": {},
            "total_size": 0,
            "created": datetime.now().isoformat(),
            "last_cleanup": datetime.now().isoformat(),
            "stats": {
                "hits": 0,
                "misses": 0,
                "evictions": 0
            }
        }
        
        self._save_metadata()
        logger.info("Cache cleared")

class LegacyCacheMigrator:
    """Migrate legacy cache from invoice project to licensing cache."""
    
    @staticmethod
    def migrate_invoice_cache(invoice_cache_path: str, licensing_cache: LicensingCacheManager):
        """Migrate data from invoice project cache to licensing cache."""
        if not os.path.exists(invoice_cache_path):
            logger.warning(f"Invoice cache file not found: {invoice_cache_path}")
            return
        
        try:
            with open(invoice_cache_path, 'r') as f:
                invoice_cache = json.load(f)
            
            migrated_count = 0
            for cache_key, invoice_data in invoice_cache.items():
                # Extract licensing-relevant data
                if "line_items" in invoice_data:
                    licensing_data = {
                        "source": "invoice_cache_migration",
                        "original_key": cache_key,
                        "vendor": invoice_data.get("vendor", ""),
                        "bill_to": invoice_data.get("bill_to", ""),
                        "invoice_date": invoice_data.get("invoice_date", ""),
                        "line_items": invoice_data["line_items"],
                        "total_amount": sum(item.get("total_amount", 0) for item in invoice_data["line_items"]),
                        "migrated_at": datetime.now().isoformat()
                    }
                    
                    # Create new identifier for licensing cache
                    identifier = f"migrated_{hash(cache_key) % 1000000}"
                    if licensing_cache.set(identifier, licensing_data):
                        migrated_count += 1
            
            logger.info(f"Migrated {migrated_count} entries from invoice cache")
            
        except Exception as e:
            logger.error(f"Error migrating invoice cache: {e}")

def get_cache_manager(cache_dir: str = None, max_size_mb: int = None, ttl_days: int = None) -> LicensingCacheManager:
    """Get a configured cache manager instance."""
    return LicensingCacheManager(cache_dir, max_size_mb, ttl_days)

def migrate_invoice_cache(invoice_cache_path: str = None):
    """Migrate legacy invoice cache to licensing cache."""
    if not invoice_cache_path:
        logger.warning("No invoice cache path provided. Migration skipped.")
        return
    
    cache_manager = get_cache_manager()
    LegacyCacheMigrator.migrate_invoice_cache(invoice_cache_path, cache_manager) 