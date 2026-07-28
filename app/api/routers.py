from fastapi import APIRouter

from app.api.health import health_router
from app.api.v1.event import event_router
from app.api.v1.operation import operation_router
from app.core.config import settings

router = APIRouter(
    prefix=settings.api.v1,
)

router.include_router(health_router, prefix="/health")
operation_router.include_router(event_router, prefix="/{operation_id}")
router.include_router(operation_router, prefix="/operations")
