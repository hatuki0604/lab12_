from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cafe:
    id: str
    name: str
    address: str
    rating: float
    category: str
    image_url: str
    google_maps_url: str
    ai_description: str
    embedding: list[float]


@dataclass(frozen=True)
class FeedbackEvent:
    timestamp: str
    selected_seed_cafe_ids: list[str]
    cafe_id: str
    feedback: str
