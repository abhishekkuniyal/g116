from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, dashboard, forecasts, health, history, iffco
from app.core.config import get_settings
from app.db.database import Base, engine
import app.models  # noqa: F401 - registers SQLAlchemy models

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.1.0",
    description="Backend API for the G116 fertilizer demand forecasting and sales analytics project.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(forecasts.router, prefix=settings.api_v1_prefix)
app.include_router(history.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
app.include_router(iffco.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "message": "G116 backend is running",
        "docs": "/docs",
        "health": "/health",
    }
