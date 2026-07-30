from fastapi import APIRouter

from app.api.health import health_router
from app.api.operation import operation_router
from app.api.receipt import receipt_router

router = APIRouter()

router.include_router(health_router, prefix="/health")
router.include_router(operation_router, prefix="/operations")
router.include_router(receipt_router, prefix="/receipts")
