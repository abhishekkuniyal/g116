from pydantic import BaseModel, ConfigDict


class ForecastOut(BaseModel):
    forecast_year: str
    state: str
    fertilizer_type: str
    sales_2024_25: float
    predicted_sales: float
    forecast_method: str
    forecast_basis: str

    model_config = ConfigDict(from_attributes=True)
