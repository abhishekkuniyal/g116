# G116 Backend (FastAPI + Microsoft SQL Server)

## 1. Create and activate environment

```bash
cd backend
python -m venv .venv
# Git Bash on Windows
source .venv/Scripts/activate
pip install -r requirements.txt
```

## 2. Check SQL Server ODBC driver

```bash
python -c "import pyodbc; print(pyodbc.drivers())"
```

Use an installed SQL Server driver in `.env` (recommended: ODBC Driver 18 for SQL Server).

## 3. Create database

Run `scripts/create_database.sql` in SSMS, or create a database named `g116` manually.

## 4. Configure environment

```bash
cp .env.example .env
```

Edit `DB_SERVER` if your SQL Server instance is not `localhost\\SQLEXPRESS`.

## 5. Import processed data

Run from the `backend/` directory:

```bash
python scripts/import_data.py
```

Required datasets:

- `../data/processed/final_forecast_2025_26.csv`
- `../data/processed/demand_forecasting.csv`

IFFCO-specific files are imported if present and their schema matches.

## 6. Start API

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

Useful endpoints:

- GET `/api/v1/forecasts`
- GET `/api/v1/forecasts/Uttarakhand/urea`
- GET `/api/v1/history/sales?state=Uttarakhand&fertilizer_type=urea`
- GET `/api/v1/analytics/trend?state=Uttarakhand&fertilizer_type=urea`
- GET `/api/v1/dashboard/summary`
- GET `/api/v1/dashboard/top-demand`
