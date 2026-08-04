"""InsightAI FastAPI application entrypoint."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import Base, engine
from app.routers import admin, auth, charts, chat, datasets, forecast, ml, projects, reports

settings = get_settings()

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title="InsightAI API",
    description="AI-powered data analyst backend: datasets, cleaning, ML, forecasting, chat, and reports.",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # For production, prefer Alembic migrations over create_all.
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok", "environment": settings.environment}


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(datasets.router)
app.include_router(charts.router)
app.include_router(ml.router)
app.include_router(forecast.router)
app.include_router(chat.router)
app.include_router(reports.router)
app.include_router(admin.router)
