from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class SeedCafeResponseItem(BaseModel):
    id: str
    name: str
    image_url: str
    rating: float
    address: str
    category: str
    google_maps_url: str


class SeedCafesResponse(BaseModel):
    seed_cafes: list[SeedCafeResponseItem]
    has_more: bool
    fallback_message: str | None


class SelectedSeedCafeResponseItem(BaseModel):
    id: str
    name: str
    category: str


class RecommendationResultItem(BaseModel):
    id: str
    name: str
    image_url: str
    rating: float
    address: str
    category: str
    similarity_score: float
    reason: str
    google_maps_url: str


class RecommendResponse(BaseModel):
    query_description: str
    selected_seed_cafes: list[SelectedSeedCafeResponseItem]
    results: list[RecommendationResultItem]
    has_more: bool
    fallback_message: str | None
