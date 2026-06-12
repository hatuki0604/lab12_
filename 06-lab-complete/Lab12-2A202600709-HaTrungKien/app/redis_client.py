from __future__ import annotations

import logging

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    # Test connection on startup
    redis_client.ping()
    logger.info("Connected to Redis successfully.")
except Exception as e:
    logger.warning(f"Failed to connect to Redis at {settings.redis_url}: {e}")
    # In a real app we might not want to crash if Redis is purely for rate limiting, 
    # but here we allow fallback or raise if needed.
    redis_client = None
