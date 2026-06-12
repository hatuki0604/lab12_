import time
from fastapi import HTTPException
from app.config import settings
from app.redis_client import redis_client

def check_rate_limit(key: str):
    now = time.time()
    redis_key = f"rate_limit:{key}"
    
    pipeline = redis_client.pipeline()
    # Remove older entries (older than 60 seconds)
    pipeline.zremrangebyscore(redis_key, 0, now - 60)
    # Get the current count
    pipeline.zcard(redis_key)
    # Add the current request timestamp
    pipeline.zadd(redis_key, {str(now): now})
    # Set expiration so we don't leak memory
    pipeline.expire(redis_key, 60)
    results = pipeline.execute()
    
    current_count = results[1]
    if current_count >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"},
        )
