from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import HistoricalDemand


METRIC_COLUMNS = {
    "sales": HistoricalDemand.sales_current,
    "requirement": HistoricalDemand.requirement_current,
    "availability": HistoricalDemand.availability_current,
}


def metric_rows(db: Session, metric: str, state: str | None, fertilizer_type: str | None):
    column = METRIC_COLUMNS[metric]
    stmt = select(
        HistoricalDemand.financial_year,
        HistoricalDemand.state,
        HistoricalDemand.fertilizer_type,
        column.label("value"),
    )
    if state:
        stmt = stmt.where(func.lower(HistoricalDemand.state) == state.strip().lower())
    if fertilizer_type:
        stmt = stmt.where(func.lower(HistoricalDemand.fertilizer_type) == fertilizer_type.strip().lower())
    stmt = stmt.order_by(HistoricalDemand.financial_year, HistoricalDemand.state, HistoricalDemand.fertilizer_type)
    return db.execute(stmt).mappings().all()


def trend_rows(db: Session, state: str, fertilizer_type: str):
    stmt = (
        select(HistoricalDemand)
        .where(
            func.lower(HistoricalDemand.state) == state.strip().lower(),
            func.lower(HistoricalDemand.fertilizer_type) == fertilizer_type.strip().lower(),
        )
        .order_by(HistoricalDemand.financial_year)
    )
    return list(db.scalars(stmt).all())
