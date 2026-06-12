from __future__ import annotations

import re


class ReasonService:
    _stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "because",
        "by",
        "cafe",
        "feels",
        "for",
        "has",
        "in",
        "is",
        "it",
        "many",
        "of",
        "quiet",
        "relaxing",
        "space",
        "that",
        "the",
        "this",
        "to",
        "user",
        "with",
    }

    def build_reason(
        self,
        query_description: str,
        cafe_description: str,
        category: str,
    ) -> str:
        query_tokens = self._extract_keywords(query_description)
        cafe_tokens = set(self._extract_keywords(cafe_description))
        overlap = [token for token in query_tokens if token in cafe_tokens][:3]

        if overlap:
            features = ", ".join(overlap)
            return (
                "Matches your vibe through "
                f"{features}, plus a {category.lower()} atmosphere."
            )

        return f"Matches your vibe through its {category.lower()} atmosphere."

    def _extract_keywords(self, text: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z]+", text.lower())
        seen: set[str] = set()
        keywords: list[str] = []
        for token in tokens:
            if len(token) < 4 or token in self._stop_words or token in seen:
                continue
            seen.add(token)
            keywords.append(token)
        return keywords

