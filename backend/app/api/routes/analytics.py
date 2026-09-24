from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analytics import TrendResponse
from app.services.history_service import trend_rows

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/trend", response_model=TrendResponse)
def trend(
    state: str = Query(...),
    fertilizer_type: str = Query(...),
    db: Session = Depends(get_db),
):
    rows = trend_rows(db, state, fertilizer_type)
    if not rows:
        raise HTTPException(status_code=404, detail="Trend data not found")

    return {
        "state": rows[0].state,
        "fertilizer_type": rows[0].fertilizer_type,
        "data": [
            {
                "year": row.financial_year,
                "sales": row.sales_current,
                "requirement": row.requirement_current,
                "availability": row.availability_current,
            }
            for row in rows
        ],
    }
