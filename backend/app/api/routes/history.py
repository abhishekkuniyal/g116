from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analytics import MetricPoint
from app.services.history_service import metric_rows

router = APIRouter(prefix="/history", tags=["Historical Analytics"])


def get_metric(metric: str, db: Session, state: str | None, fertilizer_type: str | None):
    rows = metric_rows(db, metric, state, fertilizer_type)
    if not rows:
        raise HTTPException(status_code=404, detail="No historical data found")
    return rows


@router.get("/sales", response_model=list[MetricPoint])
def sales(
    state: str | None = Query(default=None),
    fertilizer_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_metric("sales", db, state, fertilizer_type)


@router.get("/requirement", response_model=list[MetricPoint])
def requirement(
    state: str | None = Query(default=None),
    fertilizer_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_metric("requirement", db, state, fertilizer_type)


@router.get("/availability", response_model=list[MetricPoint])
def availability(
    state: str | None = Query(default=None),
    fertilizer_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_metric("availability", db, state, fertilizer_type)
