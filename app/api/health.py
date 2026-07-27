import logging

from fastapi import APIRouter, status

from app.schemas import HealthResponse

logger = logging.getLogger(__name__)

health_router = APIRouter(tags=["health"])


@health_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
)
async def check_health():
    """Health check endpoint to see if app is working"""
    extra = {"service": "health_router"}
    logger.debug("Health endpoint called", extra=extra)
    response = HealthResponse(
        status="ok",
        message="App is working",
    )
    return response
