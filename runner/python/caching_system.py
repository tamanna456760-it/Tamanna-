"""
🚀 TAMANNA AI - ENTERPRISE CACHING SYSTEM
Production-grade API response caching with multiple strategies
"""

import hashlib
import json
import logging
import pickle
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    data: Any
    timestamp: float
    ttl: int
    hits: int = 0
    size_bytes: int = 0


class CacheStrategy(ABC):
    """Abstract base for caching strategies"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store value in cache"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove value from cache"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear entire cache"""
        pass

    @abstractmethod
    def stats(self) -> Dict:
        """Get cache statistics"""
        pass


# ============================================================================
# 1️⃣ IN-MEMORY CACHE (Fast, thread-safe, bounded)
# ============================================================================

class MemoryCache(CacheStrategy):
    """
    Thread-safe in-memory LRU cache
    - Fast access O(1)
    - Automatic eviction of oldest entries
    - Bounded memory usage
    """

    def __init__(self, max_size_mb: int = 100):
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.hits = 0
        self.misses = 0

    def _calculate_size(self, obj: Any) -> int:
        """Estimate object size in bytes"""
        try:
            return len(pickle.dumps(obj))
        except:
            return 1024  # Default estimate

    def _evict_lru(self) -> None:
        """Remove least recently used entries"""
        while self.current_size > self.max_size_bytes and self.cache:
            key, entry = self.cache.popitem(last=False)
            self.current_size -= entry.size_bytes
            logger.debug(f"Evicted cache key: {key}")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve with LRU update"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]

            # Check expiration
            if time.time() - entry.timestamp > entry.ttl:
                del self.cache[key]
                self.current_size -= entry.size_bytes
                self.misses += 1
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.hits += 1
            self.hits += 1

            return entry.data

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store with size management"""
        with self.lock:
            size = self._calculate_size(value)

            # Remove old entry if exists
            if key in self.cache:
                self.current_size -= self.cache[key].size_bytes

            # Create entry
            entry = CacheEntry(
                data=value,
                timestamp=time.time(),
                ttl=ttl,
                size_bytes=size
            )

            self.cache[key] = entry
            self.current_size += size

            # Evict if necessary
            self._evict_lru()

    def delete(self, key: str) -> bool:
        """Remove specific key"""
        with self.lock:
            if key in self.cache:
                self.current_size -= self.cache[key].size_bytes
                del self.cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
            self.current_size = 0
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict:
        """Get performance metrics"""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0

            return {
                "strategy": "MemoryCache (LRU)",
                "entries": len(self.cache),
                "size_mb": self.current_size / (1024 * 1024),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": f"{hit_rate:.2f}%"
            }


# ============================================================================
# 2️⃣ DISK CACHE (Persistent, large capacity)
# ============================================================================

class DiskCache(CacheStrategy):
    """
    SQLite-backed persistent cache
    - Survives process restarts
    - Large capacity (limited by disk)
    - Slower than memory but durable
    """

    def __init__(self, db_path: str = "cache.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite schema"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    timestamp REAL NOT NULL,
                    ttl INTEGER NOT NULL,
                    hits INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON cache(timestamp)
            """)

            conn.commit()
            conn.close()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve with expiration check"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT value, timestamp, ttl FROM cache WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()

                if not row:
                    conn.close()
                    return None

                value_blob, timestamp, ttl = row

                # Check expiration
                if time.time() - timestamp > ttl:
                    cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
                    conn.commit()
                    conn.close()
                    return None

                # Update hits
                cursor.execute(
                    "UPDATE cache SET hits = hits + 1 WHERE key = ?",
                    (key,)
                )
                conn.commit()

                # Deserialize
                value = pickle.loads(value_blob)
                conn.close()

                return value

            except Exception as e:
                logger.error(f"Disk cache read error: {e}")
                return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store with serialization"""
        with self.lock:
            try:
                value_blob = pickle.dumps(value)
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO cache 
                    (key, value, timestamp, ttl) 
                    VALUES (?, ?, ?, ?)
                """, (key, value_blob, time.time(), ttl))

                conn.commit()
                conn.close()

            except Exception as e:
                logger.error(f"Disk cache write error: {e}")

    def delete(self, key: str) -> bool:
        """Remove specific key"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
                affected = cursor.rowcount
                conn.commit()
                conn.close()
                return affected > 0
            except Exception as e:
                logger.error(f"Disk cache delete error: {e}")
                return False

    def clear(self) -> None:
        """Clear entire cache"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache")
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Disk cache clear error: {e}")

    def stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM cache")
                count = cursor.fetchone()[0]

                cursor.execute("SELECT SUM(hits) FROM cache")
                total_hits = cursor.fetchone()[0] or 0

                conn.close()

                return {
                    "strategy": "DiskCache (SQLite)",
                    "entries": count,
                    "total_hits": total_hits,
                    "db_path": self.db_path
                }
            except Exception as e:
                logger.error(f"Disk cache stats error: {e}")
                return {}


# ============================================================================
# 3️⃣ HYBRID CACHE (Memory + Disk)
# ============================================================================

class HybridCache(CacheStrategy):
    """
    Two-tier caching system
    - L1: Fast in-memory cache
    - L2: Persistent disk cache
    - Best of both worlds
    """

    def __init__(self, memory_mb: int = 100, db_path: str = "cache.db"):
        self.l1 = MemoryCache(max_size_mb=memory_mb)
        self.l2 = DiskCache(db_path=db_path)
        self.l2_hits = 0
        self.l1_to_l2_promotion = 0

    def get(self, key: str) -> Optional[Any]:
        """Check L1, fall back to L2"""
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            return value

        # Try L2
        value = self.l2.get(key)
        if value is not None:
            self.l2_hits += 1
            # Promote to L1
            entry = None
            try:
                conn = sqlite3.connect(self.l2.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT ttl FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    ttl = row[0]
                    self.l1.set(key, value, ttl)
                    self.l1_to_l2_promotion += 1
                conn.close()
            except:
                pass

            return value

        return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Store in both tiers"""
        self.l1.set(key, value, ttl)
        self.l2.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Remove from both tiers"""
        l1_success = self.l1.delete(key)
        l2_success = self.l2.delete(key)
        return l1_success or l2_success

    def clear(self) -> None:
        """Clear both tiers"""
        self.l1.clear()
        self.l2.clear()

    def stats(self) -> Dict:
        """Combined statistics"""
        return {
            "strategy": "HybridCache (L1+L2)",
            "l1_stats": self.l1.stats(),
            "l2_stats": self.l2.stats(),
            "l2_hits": self.l2_hits,
            "l1_promotions": self.l1_to_l2_promotion
        }


# ============================================================================
# 4️⃣ CACHE KEY UTILITIES
# ============================================================================

class CacheKeyGenerator:
    """Generate normalized, collision-free cache keys"""

    @staticmethod
    def from_request(method: str, url: str, params: Dict = None, 
                     headers: Dict = None) -> str:
        """Generate key from HTTP request"""
        # Normalize URL
        url_normalized = url.strip().lower()

        # Sort parameters
        params_str = ""
        if params:
            params_str = json.dumps(params, sort_keys=True, default=str)

        # Include important headers
        header_str = ""
        if headers:
            auth_header = headers.get("Authorization", "")
            header_str = f"auth={hashlib.md5(auth_header.encode()).hexdigest()}"

        combined = f"{method}:{url_normalized}:{params_str}:{header_str}"
        return f"api:{hashlib.sha256(combined.encode()).hexdigest()}"

    @staticmethod
    def from_function(func_name: str, args: Tuple, kwargs: Dict) -> str:
        """Generate key from function call"""
        # Serialize arguments
        try:
            args_str = json.dumps(args, sort_keys=True, default=str)
            kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
        except:
            args_str = str(args)
            kwargs_str = str(kwargs)

        combined = f"{func_name}:{args_str}:{kwargs_str}"
        return f"func:{hashlib.sha256(combined.encode()).hexdigest()}"


# ============================================================================
# 5️⃣ DECORATORS
# ============================================================================

def cached(cache: CacheStrategy, ttl: int = 300, 
           key_generator: Optional[Callable] = None):
    """
    Decorator for caching function results
    
    Usage:
        memory_cache = MemoryCache()
        
        @cached(memory_cache, ttl=60)
        def expensive_api_call():
            return requests.get("...").json()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(func.__name__, args, kwargs)
            else:
                cache_key = CacheKeyGenerator.from_function(
                    func.__name__, args, kwargs
                )

            # Try cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT: {func.__name__}")
                return cached_result

            # Execute function
            logger.debug(f"Cache MISS: {func.__name__}")
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def cached_api_call(cache: CacheStrategy, ttl: int = 300):
    """
    Decorator specifically for API client methods
    
    Usage:
        @cached_api_call(hybrid_cache, ttl=60)
        def get_user_repos(self, username):
            return self.get(f"/users/{username}/repos")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate key from request details
            # Assumes self has request() or get() method
            cache_key = CacheKeyGenerator.from_request(
                method="GET",  # or extract from context
                url=f"{self.base_url}/{args[0] if args else ''}"
            )

            # Try cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"API cache HIT: {cache_key[:20]}...")
                return cached_result

            # Execute
            result = func(self, *args, **kwargs)

            # Cache only successful responses
            if hasattr(result, 'success') and result.success:
                cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


# ============================================================================
# 6️⃣ CACHE MANAGER (Easy factory)
# ============================================================================

class CacheManager:
    """Factory and manager for cache instances"""

    _instances: Dict[str, CacheStrategy] = {}

    @classmethod
    def create_memory(cls, name: str = "default", 
                      max_size_mb: int = 100) -> MemoryCache:
        """Create in-memory cache"""
        cache = MemoryCache(max_size_mb=max_size_mb)
        cls._instances[name] = cache
        logger.info(f"Created MemoryCache '{name}' ({max_size_mb}MB)")
        return cache

    @classmethod
    def create_disk(cls, name: str = "persistent",
                   db_path: str = "cache.db") -> DiskCache:
        """Create disk-based cache"""
        cache = DiskCache(db_path=db_path)
        cls._instances[name] = cache
        logger.info(f"Created DiskCache '{name}' at {db_path}")
        return cache

    @classmethod
    def create_hybrid(cls, name: str = "hybrid",
                     memory_mb: int = 100,
                     db_path: str = "cache.db") -> HybridCache:
        """Create hybrid cache"""
        cache = HybridCache(memory_mb=memory_mb, db_path=db_path)
        cls._instances[name] = cache
        logger.info(f"Created HybridCache '{name}' ({memory_mb}MB + disk)")
        return cache

    @classmethod
    def get(cls, name: str = "default") -> Optional[CacheStrategy]:
        """Retrieve cache by name"""
        return cls._instances.get(name)

    @classmethod
    def stats_all(cls) -> Dict:
        """Get stats for all caches"""
        return {name: cache.stats() 
                for name, cache in cls._instances.items()}

    @classmethod
    def clear_all(cls) -> None:
        """Clear all caches"""
        for cache in cls._instances.values():
            cache.clear()
        logger.info("All caches cleared")


# ============================================================================
# 7️⃣ BACKGROUND CLEANUP WORKER
# ============================================================================

class CacheCleanupWorker:
    """Background thread for cache maintenance"""

    def __init__(self, cache: CacheStrategy, interval_seconds: int = 300):
        self.cache = cache
        self.interval = interval_seconds
        self.running = False
        self.thread = None

    def start(self) -> None:
        """Start cleanup worker"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()
        logger.info("Cache cleanup worker started")

    def stop(self) -> None:
        """Stop cleanup worker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Cache cleanup worker stopped")

    def _cleanup_loop(self) -> None:
        """Periodic cleanup"""
        while self.running:
            try:
                stats = self.cache.stats()
                logger.debug(f"Cache stats: {stats}")
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.DEBUG)

    # Create hybrid cache
    cache = CacheManager.create_hybrid("api_cache")

    # Example decorator
    @cached(cache, ttl=60)
    def expensive_computation(x: int) -> int:
        logger.info(f"Computing expensive result for {x}...")
        time.sleep(2)
        return x * x

    # Test
    print("First call (slow):", expensive_computation(5))
    print("Second call (cached):", expensive_computation(5))

    # Stats
    print("\nCache Stats:")
    for key, stats in CacheManager.stats_all().items():
        print(f"  {key}: {stats}")
