from __future__ import annotations

import argparse
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
APP_DIR = PROJECT_DIR / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.data_checks import (  # noqa: E402
    validate_cafe_payload,
)
from utils.data_checks import load_json_list  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate backend JSON data files.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_DIR / "data",
        help="Directory containing cafes.json",
    )
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()
    cafe_records = load_json_list(data_dir / "cafes.json")
    cafe_dim = validate_cafe_payload(cafe_records)

    print(
        "Validation passed:",
        f"{len(cafe_records)} cafes, dimension={cafe_dim}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
