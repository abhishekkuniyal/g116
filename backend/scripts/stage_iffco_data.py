"""Copy and validate the two IFFCO processed CSVs into repo data/processed.

Example (Git Bash on Windows):
  uv run python scripts/stage_iffco_data.py --source "D:/IFFCO_Data_Preprocessing/processed"

This is optional because import_data.py can read directly from IFFCO_DATA_DIR.
Use this script when the team wants the two processed CSVs committed/shared.
"""
from argparse import ArgumentParser
from pathlib import Path
import shutil
import sys

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402

settings = get_settings()

FILES = {
    "iffco_production_state_year.csv": (
        {"financial_year", "state", "fertilizer_type", "production"},
        settings.expected_iffco_rows,
    ),
    "iffco_rajasthan_clean.csv": (
        {"financial_year", "district", "iffco_supply", "is_partial_year", "supply_unit"},
        settings.expected_rajasthan_rows,
    ),
}


def validate(path: Path, required: set[str], expected_rows: int) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    df = pd.read_csv(path)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
    if len(df) != expected_rows:
        raise ValueError(f"{path.name}: expected {expected_rows} rows, found {len(df)}")


def main():
    parser = ArgumentParser()
    parser.add_argument("--source", help="Directory containing the two processed IFFCO CSVs")
    parser.add_argument("--destination", default=str(REPO_ROOT / "data" / "processed"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    source_text = args.source or settings.iffco_data_dir
    if not source_text:
        raise ValueError("Provide --source or set IFFCO_DATA_DIR in .env")
    source = Path(source_text).expanduser()
    destination = Path(args.destination).expanduser()
    destination.mkdir(parents=True, exist_ok=True)

    for filename, (required, expected_rows) in FILES.items():
        src = source / filename
        dst = destination / filename
        validate(src, required, expected_rows)
        if dst.exists() and not args.force:
            raise FileExistsError(f"{dst} already exists. Use --force to overwrite.")
        shutil.copy2(src, dst)
        print(f"Copied {filename}: {expected_rows} rows -> {dst}")

    print("IFFCO datasets staged successfully.")


if __name__ == "__main__":
    main()
