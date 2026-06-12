from __future__ import annotations

import numpy as np


def normalize_embedding(values: list[float]) -> list[float]:
    array = np.asarray(values, dtype=float)
    norm = np.linalg.norm(array)
    if norm == 0:
        raise ValueError("Embedding norm cannot be zero")
    return (array / norm).tolist()


def average_embeddings(embeddings: list[list[float]]) -> list[float]:
    if not embeddings:
        raise ValueError("Expected at least one embedding")
    array = np.asarray(embeddings, dtype=float)
    mean_embedding = array.mean(axis=0)
    return normalize_embedding(mean_embedding.tolist())


def cosine_similarity(left: list[float], right: list[float]) -> float:
    left_array = np.asarray(left, dtype=float)
    right_array = np.asarray(right, dtype=float)
    denominator = np.linalg.norm(left_array) * np.linalg.norm(right_array)
    if denominator == 0:
        raise ValueError("Cosine similarity cannot be computed with zero vector")
    return float(np.dot(left_array, right_array) / denominator)

