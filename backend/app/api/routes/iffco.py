from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import IffcoProduction, RajasthanSupply

router = APIRouter(prefix="/iffco", tags=["IFFCO Analytics"])


@router.get("/production")
def production(
    state: str | None = Query(default=None),
    fertilizer_type: str | None = Query(default=None),
    financial_year: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(IffcoProduction)
    if state:
        stmt = stmt.where(func.lower(IffcoProduction.state) == state.strip().lower())
    if fertilizer_type:
        stmt = stmt.where(func.lower(IffcoProduction.fertilizer_type) == fertilizer_type.strip().lower())
    if financial_year:
        stmt = stmt.where(IffcoProduction.financial_year == financial_year)
    rows = db.scalars(stmt.order_by(IffcoProduction.financial_year, IffcoProduction.state)).all()
    return rows


@router.get("/rajasthan/supply")
def rajasthan_supply(
    district: str | None = Query(default=None),
    financial_year: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(RajasthanSupply)
    if district:
        stmt = stmt.where(func.lower(RajasthanSupply.district) == district.strip().lower())
    if financial_year:
        stmt = stmt.where(RajasthanSupply.financial_year == financial_year)
    rows = db.scalars(stmt.order_by(RajasthanSupply.financial_year, RajasthanSupply.district)).all()
    return rows
