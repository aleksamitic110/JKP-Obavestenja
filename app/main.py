from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.scheduler import scheduler, sync_schedule_async

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Import scrapers to trigger @register decorators
    import app.scrapers.implementations  # noqa: F401

    scheduler.start()
    await sync_schedule_async()
    LOGGER.info("Application started")

    yield

    # Shutdown
    scheduler.shutdown()
    await engine.dispose()
    LOGGER.info("Application stopped")


app = FastAPI(
    title="Serbia Utility Alerts",
    version="1.0.0",
    description="Multi-utility notification platform for Serbian citizens",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_URL}
