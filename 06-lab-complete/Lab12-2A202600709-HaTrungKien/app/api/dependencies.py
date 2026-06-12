from __future__ import annotations

from datetime import datetime

from fastapi import Depends, Header, HTTPException, Request

from app.core.config import get_settings
from app.redis_client import redis_client

settings = get_settings()

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != settings.agent_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return x_api_key

def get_user_id(x_user_id: str = Header("anonymous")):
    return x_user_id

def check_rate_limit(user_id: str = Depends(get_user_id)):
    if not redis_client:
        return True
    
    key = f"rate_limit:{user_id}"
    current = redis_client.get(key)
    if current and int(current) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Too Many Requests")
    
    pipe = redis_client.pipeline()
    pipe.incr(key)
    # Set expire if it's a new key
    if not current:
        pipe.expire(key, 60)
    pipe.execute()
    return True

def check_budget(user_id: str = Depends(get_user_id)):
    if not redis_client:
        return True
    
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(redis_client.get(key) or 0)
    # Estimate cost per request as $0.001
    estimated_cost = 0.001
    if current + estimated_cost > settings.monthly_budget_usd:
        raise HTTPException(status_code=402, detail="Payment Required: Monthly Budget Exceeded")
    
    redis_client.incrbyfloat(key, estimated_cost)
    # Ensure expiration is set for month key
    if current == 0:
        redis_client.expire(key, 32 * 24 * 3600)  # 32 days
    return True
