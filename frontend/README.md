# G116 React Frontend

Professional React + Vite dashboard for the **G116 Fertilizer Demand Forecasting & Sales Analytics System**.

## Backend expected

Run the FastAPI backend on:

```text
http://127.0.0.1:8000
```

The frontend consumes these existing endpoints:

- `GET /api/v1/forecasts`
- `GET /api/v1/forecasts/{state}/{fertilizer_type}`
- `GET /api/v1/history/sales`
- `GET /api/v1/history/requirement`
- `GET /api/v1/history/availability`
- `GET /api/v1/analytics/trend`
- `GET /api/v1/iffco/production`
- `GET /api/v1/iffco/rajasthan/supply`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/dashboard/top-demand`

## Setup with uv backend + npm frontend

From the repo root, keep the backend running in Terminal 1:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

In Terminal 2:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open:

```text
http://localhost:5173
```

## Environment

`.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Do not commit `.env`. `.env.example` is safe to commit.

## Production build

```bash
npm run build
```

The optimized output is generated in `dist/`.
