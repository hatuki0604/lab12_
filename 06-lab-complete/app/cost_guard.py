import time
from fastapi import HTTPException
from app.config import settings
from app.redis_client import redis_client

def check_and_record_cost(key: str, input_tokens: int, output_tokens: int):
    today = time.strftime("%Y-%m-%d")
    redis_key = f"daily_cost:{key}:{today}"
    
    current_cost = redis_client.get(redis_key)
    if current_cost and float(current_cost) >= settings.daily_budget_usd:
        raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
        
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    
    if cost > 0:
        pipeline = redis_client.pipeline()
        pipeline.incrbyfloat(redis_key, cost)
        # Expire key after 32 days to avoid leaking memory
        pipeline.expire(redis_key, 32 * 24 * 3600)
        pipeline.execute()

def get_daily_cost(key: str) -> float:
    today = time.strftime("%Y-%m-%d")
    redis_key = f"daily_cost:{key}:{today}"
    current_cost = redis_client.get(redis_key)
    return float(current_cost) if current_cost else 0.0
