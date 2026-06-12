from __future__ import annotations

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    selected_seed_cafe_ids: list[str] = Field(..., min_length=1, max_length=2)
    excluded_result_cafe_ids: list[str] = Field(default_factory=list)


class FeedbackRequest(BaseModel):
    selected_seed_cafe_ids: list[str] = Field(..., min_length=1, max_length=2)
    cafe_id: str
    feedback: str = Field(default="not_my_vibe")
