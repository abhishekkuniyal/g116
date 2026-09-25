from pydantic import BaseModel


class MetricPoint(BaseModel):
    financial_year: str
    state: str
    fertilizer_type: str
    value: float | None


class TrendPoint(BaseModel):
    year: str
    sales: float | None
    requirement: float | None
    availability: float | None


class TrendResponse(BaseModel):
    state: str
    fertilizer_type: str
    data: list[TrendPoint]


class DashboardSummary(BaseModel):
    forecast_year: str | None
    total_forecast_records: int
    historical_records: int
    iffco_production_records: int
    rajasthan_supply_records: int
    states: int
    fertilizer_types: int
    total_predicted_sales: float
    data_ready: bool
