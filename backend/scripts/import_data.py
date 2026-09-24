from pathlib import Path
import sys

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Forecast, HistoricalDemand, IffcoProduction, RajasthanSupply  # noqa: E402

DATA_DIR = REPO_ROOT / "data" / "processed"

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


def clean_value(value):
    return None if pd.isna(value) else value


def to_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def read_and_validate(filename: str, required: set[str]) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    df = pd.read_csv(path)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{filename} missing columns: {sorted(missing)}")
    return df


def import_forecasts(db):
    df = read_and_validate("final_forecast_2025_26.csv", FORECAST_REQUIRED)
    duplicates = df.duplicated(subset=["forecast_year", "state", "fertilizer_type"]).sum()
    if duplicates:
        raise ValueError(f"Forecast file has {duplicates} duplicate logical keys")

    db.query(Forecast).delete()
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
    print(f"Forecasts: {len(df)} rows imported")


def import_history(db):
    df = read_and_validate("demand_forecasting.csv", HISTORY_REQUIRED)
    duplicates = df.duplicated(subset=["financial_year", "state", "fertilizer_type"]).sum()
    if duplicates:
        raise ValueError(f"Historical file has {duplicates} duplicate logical keys")

    db.query(HistoricalDemand).delete()
    rows = []
    for r in df.to_dict(orient="records"):
        rows.append(HistoricalDemand(
            financial_year=str(r["financial_year"]),
            state=str(r["state"]),
            fertilizer_type=str(r["fertilizer_type"]).lower(),
            sales_current=float(r["sales_current"]),
            sales_lag_1=clean_value(r["sales_lag_1"]),
            requirement_current=clean_value(r["requirement_current"]),
            requirement_lag_1=clean_value(r["requirement_lag_1"]),
            availability_current=clean_value(r["availability_current"]),
            availability_lag_1=clean_value(r["availability_lag_1"]),
            iffco_production_current=clean_value(r["iffco_production_current"]),
            iffco_production_lag_1=clean_value(r["iffco_production_lag_1"]),
            iffco_production_available=to_bool(r["iffco_production_available"]),
            potential_reporting_break=to_bool(r["potential_reporting_break"]),
            target_sales=clean_value(r["target_sales"]),
        ))
    db.add_all(rows)
    print(f"Historical demand: {len(df)} rows imported")


def import_optional_iffco_production(db):
    path = DATA_DIR / "iffco_production_state_year.csv"
    if not path.exists():
        print("IFFCO production: optional file not present, skipped")
        return
    df = pd.read_csv(path)
    required = {"financial_year", "state", "fertilizer_type", "production"}
    missing = required - set(df.columns)
    if missing:
        print(f"IFFCO production: skipped; schema differs, missing {sorted(missing)}")
        return
    db.query(IffcoProduction).delete()
    db.add_all([
        IffcoProduction(
            financial_year=str(r.financial_year), state=str(r.state),
            fertilizer_type=str(r.fertilizer_type).lower(), production=clean_value(r.production),
        ) for r in df.itertuples(index=False)
    ])
    print(f"IFFCO production: {len(df)} rows imported")


def import_optional_rajasthan(db):
    path = DATA_DIR / "iffco_rajasthan_clean.csv"
    if not path.exists():
        print("Rajasthan supply: optional file not present, skipped")
        return
    df = pd.read_csv(path)
    required = {"financial_year", "district", "iffco_supply", "is_partial_year", "supply_unit"}
    missing = required - set(df.columns)
    if missing:
        print(f"Rajasthan supply: skipped; schema differs, missing {sorted(missing)}")
        return
    db.query(RajasthanSupply).delete()
    db.add_all([
        RajasthanSupply(
            financial_year=str(r.financial_year), district=str(r.district),
            iffco_supply=clean_value(r.iffco_supply), is_partial_year=to_bool(r.is_partial_year),
            supply_unit=clean_value(r.supply_unit),
        ) for r in df.itertuples(index=False)
    ])
    print(f"Rajasthan supply: {len(df)} rows imported")


def main():
    print(f"Using data folder: {DATA_DIR}")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        import_forecasts(db)
        import_history(db)
        import_optional_iffco_production(db)
        import_optional_rajasthan(db)
        db.commit()
        print("Import completed successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
