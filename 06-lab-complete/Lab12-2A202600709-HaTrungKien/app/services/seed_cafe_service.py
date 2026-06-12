from __future__ import annotations

from fastapi import HTTPException, status

from app.models.response import SeedCafeResponseItem, SeedCafesResponse
from app.repositories.cafe_repository import CafeRepository
from app.utils.id_validation import ensure_unique_ids


class SeedCafeService:
    def __init__(
        self,
        repository: CafeRepository,
        default_seed_count: int,
    ) -> None:
        self.repository = repository
        self.default_seed_count = default_seed_count
        self.default_fallback_message = (
            "We could not find more diverse vibe options from the current dataset. "
            "Please try again later or refresh the selection."
        )

    def list_seed_cafes(
        self,
        count: int | None = None,
        excluded_seed_cafe_ids: list[str] | None = None,
    ) -> SeedCafesResponse:
        selected_count = count or self.default_seed_count
        if selected_count < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="count must be at least 1",
            )

        excluded_seed_cafe_ids = excluded_seed_cafe_ids or []
        try:
            ensure_unique_ids(excluded_seed_cafe_ids, "excluded_seed_cafe_ids")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        seed_cafes = self.repository.sample_seed_cafes(
            count=selected_count,
            excluded_ids=set(excluded_seed_cafe_ids),
        )

        fallback_message = None
        if len(seed_cafes) < selected_count:
            fallback_message = self.default_fallback_message

        return SeedCafesResponse(
            seed_cafes=[
                SeedCafeResponseItem(
                    id=cafe.id,
                    name=cafe.name,
                    image_url=cafe.image_url,
                    rating=cafe.rating,
                    address=cafe.address,
                    category=cafe.category,
                    google_maps_url=cafe.google_maps_url,
                )
                for cafe in seed_cafes
            ],
            has_more=self.repository.has_more_seed_options(
                set(excluded_seed_cafe_ids) | {cafe.id for cafe in seed_cafes}
            ),
            fallback_message=fallback_message,
        )
