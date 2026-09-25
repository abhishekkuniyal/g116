from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Forecast, HistoricalDemand, IffcoProduction, RajasthanSupply

settings = get_settings()


def data_counts(db: Session) -> dict[str, int]:
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


def is_data_ready(counts: dict[str, int]) -> bool:
    expected = expected_counts()
    return all(counts[name] == expected[name] for name in expected)
