import json
from typing import Any, Dict, Optional
import redis

from app.core.config import settings

# Create Redis connection pool
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

class RedisCache:
    @staticmethod
    def get(key: str) -> Optional[Dict[str, Any]]:
        """Get data from Redis cache"""
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    def set(key: str, value: Dict[str, Any], expiry: int = 3600) -> bool:
        """Set data in Redis cache with expiry in seconds"""
        return redis_client.setex(key, expiry, json.dumps(value))

    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from Redis cache"""
        return redis_client.delete(key) > 0
        
    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from cache"""
        key = f"subscription:{subscription_id}"
        return RedisCache.get(key)

    @staticmethod
    def set_subscription(subscription_id: str, subscription_data: Dict[str, Any]) -> bool:
        """Cache subscription details"""
        key = f"subscription:{subscription_id}"
        return RedisCache.set(key, subscription_data, 3600)  # Cache for 1 hour

    @staticmethod
    def delete_subscription(subscription_id: str) -> bool:
        """Remove subscription from cache"""
        key = f"subscription:{subscription_id}"
        return RedisCache.delete(key)