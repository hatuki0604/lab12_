from __future__ import annotations

import json
from pathlib import Path

from app.models.domain import FeedbackEvent


class FeedbackRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def append(self, event: FeedbackEvent) -> None:
        line = json.dumps(
            {
                "timestamp": event.timestamp,
                "selected_seed_cafe_ids": event.selected_seed_cafe_ids,
                "cafe_id": event.cafe_id,
                "feedback": event.feedback,
            },
            ensure_ascii=True,
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"{line}\n")
