from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Forecast


def list_forecasts(db: Session, state: str | None = None, fertilizer_type: str | None = None):
    stmt = select(Forecast)
    if state:
        stmt = stmt.where(func.lower(Forecast.state) == state.strip().lower())
    if fertilizer_type:
        stmt = stmt.where(func.lower(Forecast.fertilizer_type) == fertilizer_type.strip().lower())
    stmt = stmt.order_by(Forecast.state, Forecast.fertilizer_type)
    return list(db.scalars(stmt).all())


def get_forecast(db: Session, state: str, fertilizer_type: str):
    stmt = select(Forecast).where(
        func.lower(Forecast.state) == state.strip().lower(),
        func.lower(Forecast.fertilizer_type) == fertilizer_type.strip().lower(),
    )
    return db.scalar(stmt)
