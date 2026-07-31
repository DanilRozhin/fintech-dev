import logging

from fastapi import APIRouter, Response, status

logger = logging.getLogger(__name__)

health_router = APIRouter(tags=["health"])


@health_router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def check_health(
    response: Response,
):
    """Health check endpoint to see if app is working"""
    extra = {"service": "health_router"}
    logger.debug("Health endpoint called", extra=extra)
    return {"status": "ok"}
