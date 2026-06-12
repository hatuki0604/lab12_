from __future__ import annotations

from fastapi import APIRouter

from app.models.response import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")

@router.get("/ready")
def readiness_probe():
    from app.redis_client import redis_client
    from fastapi import HTTPException
    import logging
    logger = logging.getLogger(__name__)

    try:
        if redis_client:
            redis_client.ping()
        else:
            logger.warning("Redis client is not initialized, skipping ready check")
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        raise HTTPException(status_code=503, detail="Database not ready")
    return {"status": "ready"}

