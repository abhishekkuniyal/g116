from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"
    __table_args__ = (
        UniqueConstraint("forecast_year", "state", "fertilizer_type", name="uq_forecast_year_state_fertilizer"),
        Index("ix_forecasts_state_fertilizer", "state", "fertilizer_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    forecast_year: Mapped[str] = mapped_column(String(20), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    fertilizer_type: Mapped[str] = mapped_column(String(30), nullable=False)
    sales_2024_25: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_sales: Mapped[float] = mapped_column(Float, nullable=False)
    forecast_method: Mapped[str] = mapped_column(String(100), nullable=False)
    forecast_basis: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class HistoricalDemand(Base):
    __tablename__ = "historical_demand"
    __table_args__ = (
        UniqueConstraint("financial_year", "state", "fertilizer_type", name="uq_history_year_state_fertilizer"),
        Index("ix_history_state_fertilizer_year", "state", "fertilizer_type", "financial_year"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    financial_year: Mapped[str] = mapped_column(String(20), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    fertilizer_type: Mapped[str] = mapped_column(String(30), nullable=False)
    sales_current: Mapped[float] = mapped_column(Float, nullable=False)
    sales_lag_1: Mapped[float | None] = mapped_column(Float)
    requirement_current: Mapped[float | None] = mapped_column(Float)
    requirement_lag_1: Mapped[float | None] = mapped_column(Float)
    availability_current: Mapped[float | None] = mapped_column(Float)
    availability_lag_1: Mapped[float | None] = mapped_column(Float)
    iffco_production_current: Mapped[float | None] = mapped_column(Float)
    iffco_production_lag_1: Mapped[float | None] = mapped_column(Float)
    iffco_production_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    potential_reporting_break: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    target_sales: Mapped[float | None] = mapped_column(Float)


class IffcoProduction(Base):
    __tablename__ = "iffco_production"
    __table_args__ = (Index("ix_iffco_state_fertilizer_year", "state", "fertilizer_type", "financial_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    financial_year: Mapped[str] = mapped_column(String(20), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    fertilizer_type: Mapped[str] = mapped_column(String(30), nullable=False)
    production: Mapped[float | None] = mapped_column(Float)


class RajasthanSupply(Base):
    __tablename__ = "rajasthan_supply"
    __table_args__ = (Index("ix_rajasthan_district_year", "district", "financial_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    financial_year: Mapped[str] = mapped_column(String(20), nullable=False)
    district: Mapped[str] = mapped_column(String(120), nullable=False)
    iffco_supply: Mapped[float | None] = mapped_column(Float)
    is_partial_year: Mapped[bool | None] = mapped_column(Boolean)
    supply_unit: Mapped[str | None] = mapped_column(String(60))
