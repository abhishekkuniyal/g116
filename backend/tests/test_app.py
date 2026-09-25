import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Force an isolated test DB before importing the application modules.
os.environ["DATABASE_URL"] = "sqlite+pysqlite://"
os.environ["CORS_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"

from fastapi.testclient import TestClient  # noqa: E402

from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Forecast, HistoricalDemand, IffcoProduction, RajasthanSupply  # noqa: E402


def seed_test_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add(Forecast(
            forecast_year="2025-26",
            state="Uttarakhand",
            fertilizer_type="urea",
            sales_2024_25=79.18,
            predicted_sales=79.18,
            forecast_method="Naive Persistence",
            forecast_basis="2024-25 sales",
        ))
        db.add(HistoricalDemand(
            financial_year="2024-25",
            state="Uttarakhand",
            fertilizer_type="urea",
            sales_current=79.18,
            sales_lag_1=74.53,
            requirement_current=77.0,
            requirement_lag_1=76.15,
            availability_current=91.72,
            availability_lag_1=91.83,
            iffco_production_current=None,
            iffco_production_lag_1=None,
            iffco_production_available=False,
            potential_reporting_break=False,
            target_sales=None,
        ))
        db.add(IffcoProduction(
            financial_year="2024-25",
            state="Gujarat",
            fertilizer_type="urea",
            production=12.5,
        ))
        db.add(RajasthanSupply(
            financial_year="2024-25",
            district="Jaipur",
            iffco_supply=1.25,
            is_partial_year=False,
            supply_unit="LMT",
        ))
        db.commit()
    finally:
        db.close()


def test_api_returns_real_seeded_data():
    seed_test_data()
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["database"] == "connected"
        assert health.json()["counts"] == {
            "forecasts": 1,
            "historical_demand": 1,
            "iffco_production": 1,
            "rajasthan_supply": 1,
        }
        # Test DB intentionally does not have production-sized counts.
        assert health.json()["data_ready"] is False

        forecasts = client.get("/api/v1/forecasts")
        assert forecasts.status_code == 200
        assert forecasts.json()[0]["state"] == "Uttarakhand"
        assert forecasts.json()[0]["predicted_sales"] == 79.18

        sales = client.get(
            "/api/v1/history/sales",
            params={"state": "Uttarakhand", "fertilizer_type": "urea"},
        )
        assert sales.status_code == 200
        assert sales.json()[0]["value"] == 79.18

        trend = client.get(
            "/api/v1/analytics/trend",
            params={"state": "Uttarakhand", "fertilizer_type": "urea"},
        )
        assert trend.status_code == 200
        assert trend.json()["data"][0]["availability"] == 91.72

        production = client.get("/api/v1/iffco/production")
        assert production.status_code == 200
        assert len(production.json()) == 1
        assert production.json()[0]["state"] == "Gujarat"

        supply = client.get("/api/v1/iffco/rajasthan/supply")
        assert supply.status_code == 200
        assert len(supply.json()) == 1
        assert supply.json()[0]["district"] == "Jaipur"

        summary = client.get("/api/v1/dashboard/summary")
        assert summary.status_code == 200
        body = summary.json()
        assert body["total_forecast_records"] == 1
        assert body["historical_records"] == 1
        assert body["iffco_production_records"] == 1
        assert body["rajasthan_supply_records"] == 1
        assert body["data_ready"] is False


def test_cors_allows_both_vite_local_origins():
    seed_test_data()
    with TestClient(app) as client:
        for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
            response = client.options(
                "/health",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert response.status_code == 200
            assert response.headers["access-control-allow-origin"] == origin


def test_iffco_routes_signal_unloaded_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        production = client.get("/api/v1/iffco/production")
        assert production.status_code == 503
        assert "not loaded" in production.json()["detail"].lower()

        supply = client.get("/api/v1/iffco/rajasthan/supply")
        assert supply.status_code == 503
        assert "not loaded" in supply.json()["detail"].lower()
