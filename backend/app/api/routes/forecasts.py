from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.forecast import ForecastOut
from app.services.forecast_service import get_forecast, list_forecasts

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@router.get("", response_model=list[ForecastOut])
def forecasts(
    state: str | None = Query(default=None),
    fertilizer_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = list_forecasts(db, state, fertilizer_type)
    if not rows:
        raise HTTPException(status_code=404, detail="No forecast data found")
    return rows


@router.get("/{state}/{fertilizer_type}", response_model=ForecastOut)
def forecast_by_state_and_fertilizer(
    state: str,
    fertilizer_type: str,
    db: Session = Depends(get_db),
):
    row = get_forecast(db, state, fertilizer_type)
    if not row:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return row
