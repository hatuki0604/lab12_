from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    project_dir = Path(__file__).resolve().parents[1]
    source_dir = project_dir / "tests" / "fixtures"
    (tmp_path / "cafes.json").write_text(
        (source_dir / "cafes.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "feedback.jsonl").write_text("", encoding="utf-8")

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:5500")
    monkeypatch.setenv("SEED_COUNT", "5")
    get_settings.cache_clear()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client, tmp_path

    get_settings.cache_clear()
