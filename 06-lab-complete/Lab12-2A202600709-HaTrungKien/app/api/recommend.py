from __future__ import annotations

from fastapi import APIRouter, Request

from app.models.request import RecommendRequest
from app.models.response import RecommendResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api", tags=["recommend"])


def _get_service(request: Request) -> RecommendationService:
    return request.app.state.recommendation_service


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: Request, payload: RecommendRequest) -> RecommendResponse:
    service = _get_service(request)
    return service.recommend(payload)

