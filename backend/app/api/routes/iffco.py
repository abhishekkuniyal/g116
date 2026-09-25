from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import IffcoProduction, RajasthanSupply

router = APIRouter(prefix="/iffco", tags=["IFFCO Analytics"])


def _ensure_table_loaded(db: Session, model, label: str) -> None:
    count = db.scalar(select(func.count()).select_from(model)) or 0
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{label} data is not loaded. Run scripts/import_data.py and verify the required CSV files.",
        )


@router.get("/production")
def production(
    state: str | None = Query(default=None),
    fertilizer_type: str | None = Query(default=None),
    financial_year: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    _ensure_table_loaded(db, IffcoProduction, "IFFCO production")
    stmt = select(IffcoProduction)
    if state:
        stmt = stmt.where(func.lower(IffcoProduction.state) == state.strip().lower())
    if fertilizer_type:
        stmt = stmt.where(func.lower(IffcoProduction.fertilizer_type) == fertilizer_type.strip().lower())
    if financial_year:
        stmt = stmt.where(IffcoProduction.financial_year == financial_year)
    return list(db.scalars(stmt.order_by(IffcoProduction.financial_year, IffcoProduction.state)).all())


@router.get("/rajasthan/supply")
def rajasthan_supply(
    district: str | None = Query(default=None),
    financial_year: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    _ensure_table_loaded(db, RajasthanSupply, "Rajasthan supply")
    stmt = select(RajasthanSupply)
    if district:
        stmt = stmt.where(func.lower(RajasthanSupply.district) == district.strip().lower())
    if financial_year:
        stmt = stmt.where(RajasthanSupply.financial_year == financial_year)
    return list(db.scalars(stmt.order_by(RajasthanSupply.financial_year, RajasthanSupply.district)).all())
