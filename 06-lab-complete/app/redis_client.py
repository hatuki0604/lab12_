import redis
from app.config import settings

def get_redis_client():
    if not settings.redis_url:
        # Fallback for local testing if needed, though production should use Redis
        return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    return redis.from_url(settings.redis_url, decode_responses=True)

redis_client = get_redis_client()
