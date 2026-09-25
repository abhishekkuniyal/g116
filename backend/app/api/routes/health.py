from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.readiness_service import data_counts, expected_counts, is_data_ready

router = APIRouter(tags=["Health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        counts = data_counts(db)
        ready = is_data_ready(counts)
        return {
            "status": "ok" if ready else "degraded",
            "database": "connected",
            "data_ready": ready,
            "counts": counts,
            "expected_counts": expected_counts(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc
