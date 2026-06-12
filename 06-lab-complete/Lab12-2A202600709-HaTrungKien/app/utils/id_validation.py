from __future__ import annotations


def ensure_unique_ids(ids: list[str], field_name: str) -> None:
    if len(set(ids)) != len(ids):
        raise ValueError(f"{field_name} must not contain duplicates")

