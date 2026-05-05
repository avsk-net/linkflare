from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import engine, Base
from app.routers import auth, links, redirect, analytics
from app.services.cleanup import start_cleanup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_cleanup_scheduler()
    yield


app = FastAPI(
    title="LinkFlare",
    description="URL shortener with click analytics",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(links.router)
app.include_router(analytics.router)
app.include_router(redirect.router)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
