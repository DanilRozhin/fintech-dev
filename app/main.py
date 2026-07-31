import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.routers import router as api_router
from app.clients import ProviderClient
from app.core.background_tasks import wait_for_all_tasks
from app.core.config import settings
from app.database import db_helper
from app.exceptions.handlers import register_exception_handlers
from app.logging.config import setup_logging
from app.services.recovery_service import run_recovery

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    # start
    extra = {"service": "main"}
    logger.info("Starting application", extra=extra)

    app.state.provider_client = ProviderClient(
        base_url=settings.provider.url,
    )

    await run_recovery(app.state.provider_client)

    yield

    # shutdown

    logger.info("Shutting down: waiting for in-flight provider calls...")
    await wait_for_all_tasks()
    await app.state.provider_client.close()
    await db_helper.dispose()
    logger.info("Shutdown complete", extra=extra)


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
register_exception_handlers(app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
