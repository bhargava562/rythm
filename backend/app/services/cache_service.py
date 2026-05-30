import os
import json
import time
from typing import Optional, Any

# Attempt to load Redis library
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class CacheService:
    _in_memory_cache = {}
    _redis_client = None

    @classmethod
    def get_redis_client(cls):
        """Lazy-loaded Redis client connection check."""
        if not REDIS_AVAILABLE:
            return None
        
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            return None

        if cls._redis_client is None:
            try:
                # Connection pool configuration
                cls._redis_client = redis.Redis.from_url(
                    redis_url, 
                    decode_responses=True, 
                    socket_connect_timeout=2.0
                )
                cls._redis_client.ping() # Check connection
                print("--- [CACHE] REDIS CONNECTION ESTABLISHED ---")
            except Exception as e:
                print(f"--- [CACHE] REDIS ERROR: {str(e)}. FALLING BACK TO IN-MEMORY CACHE ---")
                cls._redis_client = False # Disable Redis
        
        return cls._redis_client if cls._redis_client is not False else None

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Retrieve key value, checking for expiration."""
        client = cls.get_redis_client()
        if client:
            try:
                data = client.get(key)
                return json.loads(data) if data else None
            except Exception as e:
                print(f"[CACHE GET ERR] {str(e)}")

        # In-Memory Cache implementation
        cached = cls._in_memory_cache.get(key)
        if cached:
            val, expires = cached
            if expires is None or expires > time.time():
                return val
            # Key has expired, clean up
            del cls._in_memory_cache[key]
        return None

    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 300) -> bool:
        """Cache value under key with a Time-To-Live (TTL) expiration value."""
        client = cls.get_redis_client()
        if client:
            try:
                client.set(key, json.dumps(value), ex=ttl)
                return True
            except Exception as e:
                print(f"[CACHE SET ERR] {str(e)}")

        # In-Memory Cache implementation
        expiry = time.time() + ttl
        cls._in_memory_cache[key] = (value, expiry)
        return True

    @classmethod
    def delete(cls, key: str) -> bool:
        """Evict key from cache."""
        client = cls.get_redis_client()
        if client:
            try:
                client.delete(key)
                return True
            except Exception as e:
                print(f"[CACHE DEL ERR] {str(e)}")

        if key in cls._in_memory_cache:
            del cls._in_memory_cache[key]
            return True
        return False

    @classmethod
    def clear(cls) -> None:
        """Reset cache."""
        client = cls.get_redis_client()
        if client:
            try:
                client.flushdb()
            except Exception:
                pass
        cls._in_memory_cache.clear()
