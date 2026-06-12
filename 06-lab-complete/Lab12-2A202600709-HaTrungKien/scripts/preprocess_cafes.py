from __future__ import annotations

import argparse
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
APP_DIR = PROJECT_DIR / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from preprocess_shared import (  # noqa: E402
    generate_image_embedding,
    get_record_description,
    get_record_image,
    load_records,
    write_output,
)
from utils.data_checks import validate_cafe_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate SigLIP image embeddings for cafes and keep database captions for explanation."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_DIR / "data" / "cafes.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "data" / "cafes.json",
    )
    args = parser.parse_args()

    source_records = load_records(args.input)

    processed_records = []
    for record in source_records:
        ai_description = get_record_description(record)
        image = get_record_image(record)
        embedding = generate_image_embedding(image)
        processed_records.append(
            {
                "id": record["id"],
                "name": record["name"],
                "address": record["address"],
                "rating": record["rating"],
                "category": record["category"],
                "image_url": record["image_url"],
                "google_maps_url": record["google_maps_url"],
                "ai_description": ai_description,
                "embedding": embedding,
            }
        )

    validate_cafe_payload(processed_records)
    write_output(args.output, processed_records)
    print(f"Wrote {len(processed_records)} cafes to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
