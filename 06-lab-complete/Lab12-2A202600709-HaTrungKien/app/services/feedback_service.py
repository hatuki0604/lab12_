from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.domain import FeedbackEvent
from app.models.request import FeedbackRequest
from app.repositories.feedback_repository import FeedbackRepository
from app.utils.id_validation import ensure_unique_ids


class FeedbackService:
    def __init__(self, repository: FeedbackRepository) -> None:
        self.repository = repository

    def log_feedback(self, payload: FeedbackRequest) -> None:
        if payload.feedback != "not_my_vibe":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only not_my_vibe feedback is supported in MVP",
            )

        try:
            ensure_unique_ids(payload.selected_seed_cafe_ids, "selected_seed_cafe_ids")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        event = FeedbackEvent(
            timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            selected_seed_cafe_ids=payload.selected_seed_cafe_ids,
            cafe_id=payload.cafe_id,
            feedback=payload.feedback,
        )
        self.repository.append(event)
