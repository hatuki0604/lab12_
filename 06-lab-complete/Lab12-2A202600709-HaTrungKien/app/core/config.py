from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    data_dir: Path
    similarity_threshold: float
    max_results: int
    seed_count: int
    allowed_origins: list[str]
    agent_api_key: str
    redis_url: str
    rate_limit_per_minute: int
    monthly_budget_usd: float
    environment: str
    debug: bool
    port: int

    @property
    def cafes_path(self) -> Path:
        return self.data_dir / "cafes.json"

    @property
    def feedback_log_path(self) -> Path:
        return self.data_dir / "feedback.jsonl"


@lru_cache
def get_settings() -> Settings:
    project_dir = Path(__file__).resolve().parents[2]
    data_dir = Path(os.getenv("DATA_DIR", project_dir / "data")).resolve()
    allowed_origins_env = os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:3000,http://localhost:3000",
    )
    return Settings(
        app_name=os.getenv("APP_NAME", "AI Cafe Vibe Recommender Backend"),
        data_dir=data_dir,
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.65")),
        max_results=int(os.getenv("MAX_RESULTS", "3")),
        seed_count=int(os.getenv("SEED_COUNT", "5")),
        allowed_origins=[
            origin.strip()
            for origin in allowed_origins_env.split(",")
            if origin.strip()
        ],
        agent_api_key=os.getenv("AGENT_API_KEY", "secret-key-123"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "10")),
        monthly_budget_usd=float(os.getenv("MONTHLY_BUDGET_USD", "10.0")),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "true").lower() in ["true", "1", "yes"],
        port=int(os.getenv("PORT", "8000")),
    )
