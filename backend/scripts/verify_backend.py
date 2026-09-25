"""End-to-end backend verification against the configured SQL Server database.

Run after import_data.py. This checks real row counts and real API response bodies,
not only HTTP status codes. A separate uvicorn process is not required.
"""
from pathlib import Path
import sys

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402

settings = get_settings()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main():
    expected = {
        "forecasts": settings.expected_forecast_rows,
        "historical_demand": settings.expected_history_rows,
        "iffco_production": settings.expected_iffco_rows,
        "rajasthan_supply": settings.expected_rajasthan_rows,
    }

    with TestClient(app) as client:
        health = client.get("/health")
        require(health.status_code == 200, f"/health failed: {health.text}")
        health_body = health.json()
        require(health_body.get("data_ready") is True, f"Database is incomplete: {health_body}")
        require(health_body.get("counts") == expected, f"Unexpected DB counts: {health_body.get('counts')}")
        print("PASS /health -> database connected and all four table counts verified")

        forecasts = client.get("/api/v1/forecasts")
        require(forecasts.status_code == 200, f"forecasts failed: {forecasts.text}")
        forecast_rows = forecasts.json()
        require(len(forecast_rows) == expected["forecasts"], f"Expected 144 forecasts, got {len(forecast_rows)}")
        require(all(row.get("predicted_sales") is not None and row["predicted_sales"] >= 0 for row in forecast_rows), "Forecast API contains missing/negative predictions")
        print(f"PASS /api/v1/forecasts -> {len(forecast_rows)} real rows")

        sales = client.get("/api/v1/history/sales", params={"state": "Uttarakhand", "fertilizer_type": "urea"})
        require(sales.status_code == 200, f"history sales failed: {sales.text}")
        sales_rows = sales.json()
        require(len(sales_rows) > 0 and any(row.get("value") is not None for row in sales_rows), "Historical sales response is empty")
        print(f"PASS /api/v1/history/sales -> {len(sales_rows)} Uttarakhand/urea rows")

        trend = client.get("/api/v1/analytics/trend", params={"state": "Uttarakhand", "fertilizer_type": "urea"})
        require(trend.status_code == 200, f"trend failed: {trend.text}")
        trend_body = trend.json()
        require(len(trend_body.get("data", [])) > 0, "Trend API returned no data")
        print(f"PASS /api/v1/analytics/trend -> {len(trend_body['data'])} time-series points")

        production = client.get("/api/v1/iffco/production")
        require(production.status_code == 200, f"IFFCO production failed: {production.text}")
        production_rows = production.json()
        require(len(production_rows) == expected["iffco_production"], f"Expected 44 IFFCO rows, got {len(production_rows)}")
        print(f"PASS /api/v1/iffco/production -> {len(production_rows)} real rows")

        rajasthan = client.get("/api/v1/iffco/rajasthan/supply")
        require(rajasthan.status_code == 200, f"Rajasthan supply failed: {rajasthan.text}")
        rajasthan_rows = rajasthan.json()
        require(len(rajasthan_rows) == expected["rajasthan_supply"], f"Expected 132 Rajasthan rows, got {len(rajasthan_rows)}")
        print(f"PASS /api/v1/iffco/rajasthan/supply -> {len(rajasthan_rows)} real rows")

        summary = client.get("/api/v1/dashboard/summary")
        require(summary.status_code == 200, f"summary failed: {summary.text}")
        summary_body = summary.json()
        require(summary_body.get("total_forecast_records") == expected["forecasts"], "Summary forecast count mismatch")
        require(summary_body.get("historical_records") == expected["historical_demand"], "Summary historical count mismatch")
        require(summary_body.get("iffco_production_records") == expected["iffco_production"], "Summary IFFCO count mismatch")
        require(summary_body.get("rajasthan_supply_records") == expected["rajasthan_supply"], "Summary Rajasthan count mismatch")
        require(summary_body.get("data_ready") is True, "Summary says data is not ready")
        print("PASS /api/v1/dashboard/summary -> all completeness fields verified")

    print("\nBACKEND VERIFICATION SUCCESS: CSV -> SQL Server -> FastAPI is complete.")


if __name__ == "__main__":
    main()
