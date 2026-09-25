# G116 Backend — FastAPI + Microsoft SQL Server

This backend consumes the **existing forecasting outputs**. It does not change or retrain the forecasting methodology.

Required end-to-end data:

| Table | Source CSV | Required rows |
|---|---|---:|
| `forecasts` | `final_forecast_2025_26.csv` | 144 |
| `historical_demand` | `demand_forecasting.csv` | 1,440 |
| `iffco_production` | `iffco_production_state_year.csv` | 44 |
| `rajasthan_supply` | `iffco_rajasthan_clean.csv` | 132 |

The importer **fails clearly** if a required file/schema/count is wrong. It no longer silently skips IFFCO data.

## 1. Install with uv

From `g116/backend`:

```bash
uv venv
uv pip install -r requirements.txt
```

You do not need to activate the environment when using `uv run`.

## 2. Check SQL Server components

Check ODBC drivers:

```bash
uv run python -c "import pyodbc; print(pyodbc.drivers())"
```

Recommended:

```text
ODBC Driver 18 for SQL Server
```

### If using SQL Server LocalDB

Check instances:

```bash
sqllocaldb info
```

If `MSSQLLocalDB` exists:

```bash
sqllocaldb start MSSQLLocalDB
```

Use:

```env
DB_SERVER=(localdb)\MSSQLLocalDB
DB_DRIVER=ODBC Driver 18 for SQL Server
```

### If using SQL Server Express

Only use this if that instance actually exists:

```env
DB_SERVER=localhost\SQLEXPRESS
```

### If using another SQL Server instance

Set `DB_SERVER` to that real server/instance. Nothing in the backend requires `SQLEXPRESS` specifically.

## 3. Configure `.env`

```bash
cp .env.example .env
```

For the laptop described by the team, a suitable starting point is:

```env
DB_SERVER=(localdb)\MSSQLLocalDB
DB_NAME=g116
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_ENCRYPT=yes
DB_TRUST_SERVER_CERTIFICATE=yes
DB_TRUSTED_CONNECTION=yes

IFFCO_DATA_DIR=D:/IFFCO_Data_Preprocessing/processed
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Do **not** commit `.env`.

## 4. IFFCO CSV location

The main two processed CSVs are expected at:

```text
<repo>/data/processed/final_forecast_2025_26.csv
<repo>/data/processed/demand_forecasting.csv
```

The two IFFCO files may either be in the same directory **or** in `IFFCO_DATA_DIR`:

```text
iffco_production_state_year.csv   -> 44 rows
iffco_rajasthan_clean.csv         -> 132 rows
```

Current external example:

```env
IFFCO_DATA_DIR=D:/IFFCO_Data_Preprocessing/processed
```

If the team wants those files inside the repo, validate/copy them with:

```bash
uv run python scripts/stage_iffco_data.py --source "D:/IFFCO_Data_Preprocessing/processed"
```

Then review the files before committing them.

## 5. Create the configured database

The creation script uses `.env` and therefore supports LocalDB, Express, or another SQL Server instance:

```bash
uv run python scripts/create_database.py
```

## 6. Import and verify all four datasets

```bash
uv run python scripts/import_data.py
```

A correct import ends with:

```text
forecasts              144 (expected 144)
historical_demand     1440 (expected 1440)
iffco_production        44 (expected 44)
rajasthan_supply       132 (expected 132)

IMPORT SUCCESS
```

If a required CSV is missing or incomplete, the importer stops and rolls back rather than creating a partially populated project database.

## 7. Run real backend verification

This checks both database completeness **and API response bodies**:

```bash
uv run python scripts/verify_backend.py
```

It verifies:

- `GET /health`
- `GET /api/v1/forecasts` -> 144 records and valid predictions
- `GET /api/v1/history/sales?state=Uttarakhand&fertilizer_type=urea` -> non-empty data
- `GET /api/v1/analytics/trend?state=Uttarakhand&fertilizer_type=urea` -> non-empty time series
- `GET /api/v1/iffco/production` -> 44 records
- `GET /api/v1/iffco/rajasthan/supply` -> 132 records
- `GET /api/v1/dashboard/summary` -> all four expected counts and `data_ready=true`

No separate uvicorn process is required for this verification script.

## 8. Start FastAPI

```bash
uv run uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

A fully populated `/health` response includes:

```json
{
  "status": "ok",
  "database": "connected",
  "data_ready": true,
  "counts": {
    "forecasts": 144,
    "historical_demand": 1440,
    "iffco_production": 44,
    "rajasthan_supply": 132
  }
}
```

## 9. React frontend

Frontend API URL remains environment-controlled:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start Vite using either `localhost:5173` or `127.0.0.1:5173`; both are allowed by the default backend CORS configuration.

## 10. Tests

```bash
uv run pytest -v
```

The test suite uses isolated SQLite for API behavior tests. Use `scripts/verify_backend.py` for the real SQL Server/data integration test.
