from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_CAFE_FIELDS = {
    "id",
    "name",
    "address",
    "rating",
    "category",
    "image_url",
    "google_maps_url",
    "ai_description",
    "embedding",
}


def load_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Data file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON list in {path}")
    if not payload:
        raise ValueError(f"Expected non-empty data list in {path}")
    return payload

def validate_cafe_payload(records: list[dict[str, Any]]) -> int:
    embedding_dim = _validate_records(records, REQUIRED_CAFE_FIELDS, "cafe")
    for record in records:
        image_url = record["image_url"]
        if not isinstance(image_url, str) or not image_url.strip():
            raise ValueError(f"cafe {record['id']} has invalid image_url")
    return embedding_dim


def _validate_records(
    records: list[dict[str, Any]],
    required_fields: set[str],
    label: str,
) -> int:
    seen_ids: set[str] = set()
    embedding_dim: int | None = None

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{label} at index {index} must be an object")

        missing = required_fields - record.keys()
        if missing:
            raise ValueError(
                f"{label} at index {index} missing fields: {sorted(missing)}"
            )

        record_id = record["id"]
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"{label} at index {index} has invalid id")
        if record_id in seen_ids:
            raise ValueError(f"Duplicate {label} id found: {record_id}")
        seen_ids.add(record_id)

        embedding = record["embedding"]
        if not isinstance(embedding, list) or not embedding:
            raise ValueError(f"{label} {record_id} has empty embedding")
        if not all(isinstance(value, (int, float)) for value in embedding):
            raise ValueError(f"{label} {record_id} has non-numeric embedding values")

        if embedding_dim is None:
            embedding_dim = len(embedding)
        elif len(embedding) != embedding_dim:
            raise ValueError(
                f"{label} {record_id} has embedding dimension {len(embedding)}; "
                f"expected {embedding_dim}"
            )

    if embedding_dim is None:
        raise ValueError(f"No embeddings found for {label} records")
    return embedding_dim
