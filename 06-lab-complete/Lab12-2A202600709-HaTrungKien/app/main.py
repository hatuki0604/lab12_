from __future__ import annotations

from contextlib import asynccontextmanager
import time
import json
import signal
import logging

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.feedback import router as feedback_router
from app.api.health import router as health_router
from app.api.recommend import router as recommend_router
from app.api.seed_cafes import router as seed_cafes_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.repositories.cafe_repository import CafeRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.services.feedback_service import FeedbackService
from app.services.reason_service import ReasonService
from app.services.recommendation_service import RecommendationService
from app.services.seed_cafe_service import SeedCafeService


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()

    cafe_repository = CafeRepository(settings.cafes_path)
    feedback_repository = FeedbackRepository(settings.feedback_log_path)

    app.state.seed_cafe_service = SeedCafeService(
        repository=cafe_repository,
        default_seed_count=settings.seed_count,
    )
    app.state.recommendation_service = RecommendationService(
        cafe_repository=cafe_repository,
        reason_service=ReasonService(),
        similarity_threshold=settings.similarity_threshold,
        max_results=settings.max_results,
    )
    app.state.feedback_service = FeedbackService(feedback_repository)

    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        start = time.time()
        logger = logging.getLogger("request_middleware")
        try:
            response: Response = await call_next(request)
            duration = round((time.time() - start) * 1000, 1)
            logger.info(json.dumps({
                "event": "request",
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "ms": duration,
            }))
            return response
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            raise

    from app.api.dependencies import verify_api_key, check_rate_limit, check_budget
    protected_deps = [
        Depends(verify_api_key),
        Depends(check_rate_limit),
        Depends(check_budget),
    ]

    app.include_router(health_router)
    app.include_router(seed_cafes_router, dependencies=protected_deps)
    app.include_router(recommend_router, dependencies=protected_deps)
    app.include_router(feedback_router, dependencies=protected_deps)
    
    import os
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    if os.path.exists("frontend"):
        app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
    if os.path.exists("data"):
        app.mount("/data", StaticFiles(directory="data"), name="data")
        
    @app.get("/")
    async def serve_index():
        if os.path.exists("index.html"):
            return FileResponse("index.html")
        return {"message": "API is running but index.html not found"}

    return app

def _handle_signal(signum, _frame):
    logger = logging.getLogger(__name__)
    logger.info(json.dumps({"event": "signal", "signum": signum, "message": "Graceful shutdown initiated"}))

signal.signal(signal.SIGTERM, _handle_signal)

app = create_app()
