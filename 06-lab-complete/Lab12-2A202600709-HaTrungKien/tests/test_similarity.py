from __future__ import annotations

from app.utils.similarity import average_embeddings, cosine_similarity, normalize_embedding


def test_normalize_embedding_returns_unit_length():
    normalized = normalize_embedding([3.0, 4.0])
    assert round(sum(value * value for value in normalized), 5) == 1.0


def test_average_embeddings_normalizes_output():
    averaged = average_embeddings([[1.0, 0.0], [0.0, 1.0]])
    assert round(sum(value * value for value in averaged), 5) == 1.0


def test_cosine_similarity_detects_perfect_match():
    assert round(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 5) == 1.0
