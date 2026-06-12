from __future__ import annotations

import random
from pathlib import Path

from app.models.domain import Cafe
from app.utils.data_checks import load_json_list, validate_cafe_payload
from app.utils.similarity import normalize_embedding


class CafeRepository:
    def __init__(self, path: Path) -> None:
        payload = load_json_list(path)
        validate_cafe_payload(payload)
        self._items = [
            Cafe(
                id=record["id"],
                name=record["name"],
                address=record["address"],
                rating=float(record["rating"]),
                category=record["category"],
                image_url=record["image_url"],
                google_maps_url=record["google_maps_url"],
                ai_description=record["ai_description"],
                embedding=normalize_embedding(record["embedding"]),
            )
            for record in payload
        ]
        self._items_by_id = {cafe.id: cafe for cafe in self._items}
        self._cafes_by_category: dict[str, list[Cafe]] = {}
        for cafe in self._items:
            self._cafes_by_category.setdefault(cafe.category, []).append(cafe)

    def list_available(self, excluded_ids: set[str] | None = None) -> list[Cafe]:
        excluded_ids = excluded_ids or set()
        return [cafe for cafe in self._items if cafe.id not in excluded_ids]

    def get_many(self, ids: list[str]) -> list[Cafe]:
        cafes: list[Cafe] = []
        for cafe_id in ids:
            cafe = self._items_by_id.get(cafe_id)
            if cafe is None:
                raise KeyError(cafe_id)
            cafes.append(cafe)
        return cafes

    def sample_seed_cafes(
        self,
        count: int,
        excluded_ids: set[str] | None = None,
    ) -> list[Cafe]:
        excluded_ids = excluded_ids or set()
        available_by_category: dict[str, list[Cafe]] = {}
        for category, cafes in self._cafes_by_category.items():
            available = [cafe for cafe in cafes if cafe.id not in excluded_ids]
            if available:
                available_by_category[category] = available

        categories = list(available_by_category.keys())
        if not categories:
            return []

        selected_categories = random.sample(categories, k=min(count, len(categories)))
        seed_cafes = [
            random.choice(available_by_category[category])
            for category in selected_categories
        ]
        seed_cafes.sort(key=lambda cafe: cafe.category)
        return seed_cafes

    def has_more_seed_options(
        self,
        current_seed_ids: set[str],
    ) -> bool:
        return any(cafe.id not in current_seed_ids for cafe in self._items)
