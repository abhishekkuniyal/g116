from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Forecast
from app.schemas.analytics import DashboardSummary
from app.services.readiness_service import data_counts, is_data_ready

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    counts = data_counts(db)
    states = db.scalar(select(func.count(distinct(Forecast.state)))) or 0
    fertilizers = db.scalar(select(func.count(distinct(Forecast.fertilizer_type)))) or 0
    total_predicted = db.scalar(select(func.coalesce(func.sum(Forecast.predicted_sales), 0.0))) or 0.0
    year = db.scalar(select(Forecast.forecast_year).limit(1))

    return {
        "forecast_year": year,
        "total_forecast_records": counts["forecasts"],
        "historical_records": counts["historical_demand"],
        "iffco_production_records": counts["iffco_production"],
        "rajasthan_supply_records": counts["rajasthan_supply"],
        "states": states,
        "fertilizer_types": fertilizers,
        "total_predicted_sales": float(total_predicted),
        "data_ready": is_data_ready(counts),
    }


@router.get("/top-demand")
def top_demand(limit: int = 10, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 100))
    stmt = select(Forecast).order_by(Forecast.predicted_sales.desc()).limit(limit)
    rows = db.scalars(stmt).all()
    return [
        {
            "state": row.state,
            "fertilizer_type": row.fertilizer_type,
            "predicted_sales": row.predicted_sales,
            "forecast_year": row.forecast_year,
        }
        for row in rows
    ]
