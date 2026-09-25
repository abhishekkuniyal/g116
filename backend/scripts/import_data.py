from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import func, select

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402
from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Forecast, HistoricalDemand, IffcoProduction, RajasthanSupply  # noqa: E402

settings = get_settings()
PRIMARY_DATA_DIR = settings.configured_data_dir(REPO_ROOT)
IFFCO_DATA_DIR = settings.configured_iffco_data_dir

FORECAST_REQUIRED = {
    "forecast_year", "state", "fertilizer_type", "sales_2024_25",
    "predicted_sales", "forecast_method", "forecast_basis",
}

HISTORY_REQUIRED = {
    "financial_year", "state", "fertilizer_type", "sales_current", "sales_lag_1",
    "requirement_current", "requirement_lag_1", "availability_current",
    "availability_lag_1", "iffco_production_current", "iffco_production_lag_1",
    "iffco_production_available", "potential_reporting_break", "target_sales",
}

IFFCO_REQUIRED = {"financial_year", "state", "iffco_fertiliser_type", "iffco_production"}
RAJASTHAN_REQUIRED = {"financial_year", "district", "iffco_supply", "is_partial_year", "supply_unit"}


def clean_value(value):
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def clean_float(value):
    value = clean_value(value)
    return None if value is None else float(value)


def to_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def source_dirs(filename: str) -> list[Path]:
    dirs: list[Path] = []
    if filename in {"iffco_production_state_year.csv", "iffco_rajasthan_clean.csv"} and IFFCO_DATA_DIR:
        dirs.append(IFFCO_DATA_DIR)
    dirs.append(PRIMARY_DATA_DIR)

    unique: list[Path] = []
    seen: set[str] = set()
    for directory in dirs:
        key = str(directory.resolve()) if directory.exists() else str(directory)
        if key not in seen:
            seen.add(key)
            unique.append(directory)
    return unique


def resolve_source(filename: str) -> Path:
    searched = []
    for directory in source_dirs(filename):
        path = directory / filename
        searched.append(str(path))
        if path.exists():
            return path
    raise FileNotFoundError(
        f"Missing required file: {filename}. Searched: {searched}. "
        "Set DATA_DIR and/or IFFCO_DATA_DIR in backend/.env if the processed CSVs live elsewhere."
    )


def read_and_validate(filename: str, required: set[str], expected_rows: int) -> tuple[pd.DataFrame, Path]:
    path = resolve_source(filename)
    df = pd.read_csv(path)

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{filename} missing columns: {sorted(missing)}")

    if settings.strict_import_counts and len(df) != expected_rows:
        raise ValueError(
            f"{filename} has {len(df)} rows; expected exactly {expected_rows}. "
            "Refusing to build an incomplete project database."
        )

    print(f"Source: {filename} -> {path} ({len(df)} rows)")
    return df, path


def assert_no_null_keys(df: pd.DataFrame, filename: str, columns: list[str]) -> None:
    bad = df[columns].isna().any(axis=1).sum()
    if bad:
        raise ValueError(f"{filename} has {bad} rows with missing key fields: {columns}")


def assert_no_duplicates(df: pd.DataFrame, filename: str, columns: list[str]) -> None:
    duplicates = int(df.duplicated(subset=columns).sum())
    if duplicates:
        raise ValueError(f"{filename} has {duplicates} duplicate logical keys for {columns}")


def import_forecasts(db):
    filename = "final_forecast_2025_26.csv"
    df, _ = read_and_validate(filename, FORECAST_REQUIRED, settings.expected_forecast_rows)
    key = ["forecast_year", "state", "fertilizer_type"]
    assert_no_null_keys(df, filename, key)
    assert_no_duplicates(df, filename, key)

    if df["predicted_sales"].isna().any():
        raise ValueError(f"{filename} contains missing predictions")
    if (pd.to_numeric(df["predicted_sales"], errors="raise") < 0).any():
        raise ValueError(f"{filename} contains negative predictions")

    db.query(Forecast).delete(synchronize_session=False)
    db.add_all([
        Forecast(
            forecast_year=str(r.forecast_year),
            state=str(r.state),
            fertilizer_type=str(r.fertilizer_type).lower(),
            sales_2024_25=float(r.sales_2024_25),
            predicted_sales=float(r.predicted_sales),
            forecast_method=str(r.forecast_method),
            forecast_basis=str(r.forecast_basis),
        )
        for r in df.itertuples(index=False)
    ])
    print(f"Forecasts: {len(df)} rows staged")


def import_history(db):
    filename = "demand_forecasting.csv"
    df, _ = read_and_validate(filename, HISTORY_REQUIRED, settings.expected_history_rows)
    key = ["financial_year", "state", "fertilizer_type"]
    assert_no_null_keys(df, filename, key)
    assert_no_duplicates(df, filename, key)

    db.query(HistoricalDemand).delete(synchronize_session=False)
    rows = []
    for r in df.to_dict(orient="records"):
        rows.append(HistoricalDemand(
            financial_year=str(r["financial_year"]),
            state=str(r["state"]),
            fertilizer_type=str(r["fertilizer_type"]).lower(),
            sales_current=float(r["sales_current"]),
            sales_lag_1=clean_float(r["sales_lag_1"]),
            requirement_current=clean_float(r["requirement_current"]),
            requirement_lag_1=clean_float(r["requirement_lag_1"]),
            availability_current=clean_float(r["availability_current"]),
            availability_lag_1=clean_float(r["availability_lag_1"]),
            iffco_production_current=clean_float(r["iffco_production_current"]),
            iffco_production_lag_1=clean_float(r["iffco_production_lag_1"]),
            iffco_production_available=to_bool(r["iffco_production_available"]),
            potential_reporting_break=to_bool(r["potential_reporting_break"]),
            target_sales=clean_float(r["target_sales"]),
        ))
    db.add_all(rows)
    print(f"Historical demand: {len(df)} rows staged")


def import_iffco_production(db):
    filename = "iffco_production_state_year.csv"
    df, _ = read_and_validate(filename, IFFCO_REQUIRED, settings.expected_iffco_rows)

    # The forecasting pipeline intentionally outputs IFFCO-specific column names.
    # Normalize them only at the backend import boundary; do not alter source data.
    df = df.rename(columns={
        "iffco_fertiliser_type": "fertilizer_type",
        "iffco_production": "production",
    })

    key = ["financial_year", "state", "fertilizer_type"]
    assert_no_null_keys(df, filename, key)
    assert_no_duplicates(df, filename, key)

    db.query(IffcoProduction).delete(synchronize_session=False)
    db.add_all([
        IffcoProduction(
            financial_year=str(r.financial_year),
            state=str(r.state),
            fertilizer_type=str(r.fertilizer_type).lower(),
            production=clean_float(r.production),
        )
        for r in df.itertuples(index=False)
    ])
    print(f"IFFCO production: {len(df)} rows staged")


def import_rajasthan(db):
    filename = "iffco_rajasthan_clean.csv"
    df, _ = read_and_validate(filename, RAJASTHAN_REQUIRED, settings.expected_rajasthan_rows)
    key = ["financial_year", "district"]
    assert_no_null_keys(df, filename, key)
    assert_no_duplicates(df, filename, key)

    db.query(RajasthanSupply).delete(synchronize_session=False)
    db.add_all([
        RajasthanSupply(
            financial_year=str(r.financial_year),
            district=str(r.district),
            iffco_supply=clean_float(r.iffco_supply),
            is_partial_year=to_bool(r.is_partial_year),
            supply_unit=None if pd.isna(r.supply_unit) else str(r.supply_unit),
        )
        for r in df.itertuples(index=False)
    ])
    print(f"Rajasthan supply: {len(df)} rows staged")


def actual_counts(db) -> dict[str, int]:
    return {
        "forecasts": db.scalar(select(func.count()).select_from(Forecast)) or 0,
        "historical_demand": db.scalar(select(func.count()).select_from(HistoricalDemand)) or 0,
        "iffco_production": db.scalar(select(func.count()).select_from(IffcoProduction)) or 0,
        "rajasthan_supply": db.scalar(select(func.count()).select_from(RajasthanSupply)) or 0,
    }


def expected_counts() -> dict[str, int]:
    return {
        "forecasts": settings.expected_forecast_rows,
        "historical_demand": settings.expected_history_rows,
        "iffco_production": settings.expected_iffco_rows,
        "rajasthan_supply": settings.expected_rajasthan_rows,
    }


def verify_counts(db) -> dict[str, int]:
    db.flush()
    actual = actual_counts(db)
    expected = expected_counts()
    print("\nDatabase row-count verification:")
    for table, count in actual.items():
        print(f"  {table:<20} {count:>5} (expected {expected[table]})")

    mismatches = {
        table: {"actual": actual[table], "expected": expected[table]}
        for table in expected
        if actual[table] != expected[table]
    }
    if mismatches:
        raise ValueError(f"Database completeness check failed: {mismatches}")
    return actual


def main():
    print(f"Primary data folder: {PRIMARY_DATA_DIR}")
    if IFFCO_DATA_DIR:
        print(f"IFFCO data folder:   {IFFCO_DATA_DIR}")
    print(f"Strict row counts:   {settings.strict_import_counts}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        import_forecasts(db)
        import_history(db)
        import_iffco_production(db)
        import_rajasthan(db)
        verify_counts(db)
        db.commit()
        print("\nIMPORT SUCCESS: all four required datasets are loaded and verified.")
    except Exception as exc:
        db.rollback()
        print(f"\nIMPORT FAILED: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
