import logging
from contextlib import asynccontextmanager

import uvicorn
from api.routers import router as api_router
from database import db_helper
from fastapi import FastAPI

from app.core.config import settings
from app.exceptions.handlers import register_exception_handlers
from app.logging.config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    # start
    extra = {"service": "main"}
    logger.info("Starting application", extra=extra)
    yield
    # shutdown
    await db_helper.dispose()
    logger.info("Finishing application", extra=extra)


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix=settings.api.prefix)
register_exception_handlers(app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
