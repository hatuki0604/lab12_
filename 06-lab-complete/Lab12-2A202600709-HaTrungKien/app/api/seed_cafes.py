from __future__ import annotations

from fastapi import APIRouter, Query, Request

from app.models.response import SeedCafesResponse
from app.services.seed_cafe_service import SeedCafeService

router = APIRouter(prefix="/api", tags=["seed-cafes"])


def _get_service(request: Request) -> SeedCafeService:
    return request.app.state.seed_cafe_service


@router.get("/seed-cafes", response_model=SeedCafesResponse)
def get_seed_cafes(
    request: Request,
    count: int | None = Query(default=None, ge=1, le=10),
    excluded_seed_cafe_ids: list[str] | None = Query(default=None),
) -> SeedCafesResponse:
    service = _get_service(request)
    return service.list_seed_cafes(
        count=count,
        excluded_seed_cafe_ids=excluded_seed_cafe_ids,
    )
