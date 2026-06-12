from __future__ import annotations

import io
import json
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import requests
import torch
from dotenv import load_dotenv
from PIL import Image
from transformers import SiglipImageProcessor, SiglipVisionModel


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
APP_DIR = PROJECT_DIR / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.data_checks import load_json_list  # noqa: E402
from utils.similarity import normalize_embedding  # noqa: E402


DESCRIPTION_FIELDS = (
    "ai_description",
    "caption",
    "description",
    "image_caption",
    "caption_text",
)

load_dotenv(PROJECT_DIR / ".env")


def get_siglip_model_name() -> str:
    return os.getenv("SIGLIP_MODEL_NAME", "google/siglip-base-patch16-224")


def get_siglip_device() -> str:
    configured = os.getenv("SIGLIP_DEVICE")
    if configured:
        return configured
    return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def load_siglip_components() -> tuple[SiglipVisionModel, SiglipImageProcessor, str]:
    model_name = get_siglip_model_name()
    device = get_siglip_device()
    model = SiglipVisionModel.from_pretrained(model_name)
    model.eval()
    model.to(device)
    processor = SiglipImageProcessor.from_pretrained(model_name)
    return model, processor, device


def load_records(path: Path) -> list[dict[str, Any]]:
    resolved = path.resolve()
    if resolved.suffix == ".jsonl":
        records: list[dict[str, Any]] = []
        for line_number, line in enumerate(
            resolved.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSONL at {resolved}:{line_number}: {exc}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(f"Expected JSON object in {resolved}:{line_number}")
            records.append(record)
        if not records:
            raise ValueError(f"Expected non-empty JSONL data in {resolved}")
        return records

    return load_json_list(resolved)


def get_record_description(record: dict[str, Any]) -> str:
    for field_name in DESCRIPTION_FIELDS:
        value = record.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()

    record_id = record.get("id", "<unknown>")
    raise ValueError(
        f"Record {record_id} must contain one of the description fields: "
        f"{', '.join(DESCRIPTION_FIELDS)}"
    )


def get_record_image(record: dict[str, Any]) -> Image.Image:
    source_path = record.get("source_image_path")
    if isinstance(source_path, str) and source_path.strip():
        image_path = Path(source_path)
        if not image_path.is_absolute():
            image_path = (PROJECT_DIR / image_path).resolve()
        if not image_path.exists():
            raise ValueError(f"Image file not found: {image_path}")
        return Image.open(image_path).convert("RGB")

    for field_name in ("source_image_url", "image_url"):
        value = record.get(field_name)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            response = requests.get(value, timeout=30)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content)).convert("RGB")

    record_id = record.get("id", "<unknown>")
    raise ValueError(
        f"Record {record_id} must define source_image_path, source_image_url, "
        "or an absolute image_url for SigLIP preprocessing"
    )


def generate_image_embedding(image: Image.Image) -> list[float]:
    model, processor, device = load_siglip_components()
    inputs = processor(images=image, return_tensors="pt")
    pixel_values = inputs["pixel_values"].to(device)

    with torch.no_grad():
        outputs = model(pixel_values=pixel_values)
        embedding = outputs.pooler_output[0].detach().cpu().tolist()

    return normalize_embedding(embedding)


def write_output(path: Path, records: list[dict[str, Any]]) -> None:
    path.resolve().write_text(
        json.dumps(records, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
