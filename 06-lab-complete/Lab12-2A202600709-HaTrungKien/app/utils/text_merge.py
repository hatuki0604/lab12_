from __future__ import annotations


def combine_descriptions(descriptions: list[str]) -> str:
    cleaned = [description.strip() for description in descriptions if description.strip()]
    if not cleaned:
        raise ValueError("Expected at least one description")
    if len(cleaned) == 1:
        return cleaned[0]
    return (
        "The user prefers a cafe vibe that combines these qualities: "
        + " ".join(cleaned)
    )

