from __future__ import annotations

from fastapi import HTTPException, status

from app.models.domain import Cafe
from app.models.request import RecommendRequest
from app.models.response import (
    RecommendResponse,
    RecommendationResultItem,
    SelectedSeedCafeResponseItem,
)
from app.repositories.cafe_repository import CafeRepository
from app.services.reason_service import ReasonService
from app.utils.id_validation import ensure_unique_ids
from app.utils.similarity import average_embeddings, cosine_similarity
from app.utils.text_merge import combine_descriptions


class RecommendationService:
    def __init__(
        self,
        cafe_repository: CafeRepository,
        reason_service: ReasonService,
        similarity_threshold: float,
        max_results: int = 3,
    ) -> None:
        self.cafe_repository = cafe_repository
        self.reason_service = reason_service
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        self.default_fallback_message = (
            "We could not find a very close match, but here are the nearest "
            "options from our current dataset."
        )

    def recommend(self, payload: RecommendRequest) -> RecommendResponse:
        try:
            ensure_unique_ids(payload.selected_seed_cafe_ids, "selected_seed_cafe_ids")
            ensure_unique_ids(
                payload.excluded_result_cafe_ids,
                "excluded_result_cafe_ids",
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        try:
            selected_seed_cafes = self.cafe_repository.get_many(payload.selected_seed_cafe_ids)
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown seed cafe id: {exc.args[0]}",
            ) from exc

        query_description, query_embedding = self._build_query(selected_seed_cafes)
        excluded_ids = set(payload.excluded_result_cafe_ids) | {
            cafe.id for cafe in selected_seed_cafes
        }
        cafes = self.cafe_repository.list_available(excluded_ids)

        if not cafes:
            return RecommendResponse(
                query_description=query_description,
                selected_seed_cafes=self._selected_seed_cafes_payload(selected_seed_cafes),
                results=[],
                has_more=False,
                fallback_message=self.default_fallback_message,
            )

        scored_results: list[tuple[float, RecommendationResultItem]] = []
        for cafe in cafes:
            similarity_score = round(
                cosine_similarity(query_embedding, cafe.embedding),
                4,
            )
            scored_results.append(
                (
                    similarity_score,
                    RecommendationResultItem(
                        id=cafe.id,
                        name=cafe.name,
                        image_url=cafe.image_url,
                        rating=cafe.rating,
                        address=cafe.address,
                        category=cafe.category,
                        similarity_score=similarity_score,
                        reason=self.reason_service.build_reason(
                            query_description=query_description,
                            cafe_description=cafe.ai_description,
                            category=cafe.category,
                        ),
                        google_maps_url=cafe.google_maps_url,
                    ),
                )
            )

        scored_results.sort(key=lambda item: item[0], reverse=True)
        top_results = [result for _, result in scored_results[: self.max_results]]
        top_score = scored_results[0][0] if scored_results else 0.0

        fallback_message = None
        if top_score < self.similarity_threshold or len(top_results) < self.max_results:
            fallback_message = self.default_fallback_message

        return RecommendResponse(
            query_description=query_description,
            selected_seed_cafes=self._selected_seed_cafes_payload(selected_seed_cafes),
            results=top_results,
            has_more=len(scored_results) > len(top_results),
            fallback_message=fallback_message,
        )

    def _build_query(self, selected_cafes: list[Cafe]) -> tuple[str, list[float]]:
        descriptions = [cafe.ai_description for cafe in selected_cafes]
        embeddings = [cafe.embedding for cafe in selected_cafes]
        if len(embeddings) == 1:
            return combine_descriptions(descriptions), embeddings[0]
        return combine_descriptions(descriptions), average_embeddings(embeddings)

    def _selected_seed_cafes_payload(
        self,
        cafes: list[Cafe],
    ) -> list[SelectedSeedCafeResponseItem]:
        return [
            SelectedSeedCafeResponseItem(
                id=cafe.id,
                name=cafe.name,
                category=cafe.category,
            )
            for cafe in cafes
        ]
