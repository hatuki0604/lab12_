from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
SUPABASE_CAFES_TABLE = os.getenv("SUPABASE_CAFES_TABLE", "cafes")

if not SUPABASE_URL:
    raise RuntimeError("Missing SUPABASE_URL in environment variables")

if not SUPABASE_PUBLISHABLE_KEY:
    raise RuntimeError("Missing SUPABASE_PUBLISHABLE_KEY in environment variables")


def get_cafes() -> list[dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_CAFES_TABLE}"
    headers = {
        "apikey": SUPABASE_PUBLISHABLE_KEY,
    }
    params = {
        "select": "*",
        "order": "id.asc",
    }
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise RuntimeError("Supabase response is not a list")
    return data


def export_cafes_jsonl(output_path: str = "data/cafes.jsonl") -> Path:
    cafes = get_cafes()
    path = PROJECT_DIR / output_path
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for cafe in cafes:
            file.write(json.dumps(cafe, ensure_ascii=False) + "\n")

    return path


if __name__ == "__main__":
    cafes = get_cafes()
    print(f"Loaded {len(cafes)} cafes")
    for cafe in cafes[:3]:
        print(cafe)

    output_file = export_cafes_jsonl()
    print(f"Exported JSONL to: {output_file.resolve()}")
