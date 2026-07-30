import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.errors import (
    BaseAppError,
    DatabaseError,
    OperationError,
    ProviderPaymentIdMismatchError,
    ValidationObjectError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProviderPaymentIdMismatchError)
    def provider_payment_id_mismatch_error_handler(req: Request, exc: ProviderPaymentIdMismatchError) -> JSONResponse:
        logger.error(
            msg=exc.detail,
            exc_info=exc.__cause__,
            extra={
                "extra_info": exc.extra,
                "content": str(exc.__class__.__name__),
                "path": req.url.path,
                "method": req.method,
                "service": exc.extra.get("service", "unknown"),
            },
        )
        return JSONResponse(
            content={
                "detail": exc.detail,
                "provider_payment_id": exc.extra.get("provider_payment_id"),
                "operation_id": exc.extra.get("operation_id"),
            },
            status_code=exc.status_code,
        )

    @app.exception_handler(ValidationObjectError)
    def validation_object_error_handler(req: Request, exc: ValidationObjectError) -> JSONResponse:
        logger.error(
            msg=exc.detail,
            exc_info=exc.__cause__,
            extra={
                "extra_info": exc.extra,
                "content": str(exc.__class__.__name__),
                "path": req.url.path,
                "method": req.method,
                "service": exc.extra.get("service", "unknown"),
            },
        )
        return JSONResponse(
            content={
                "detail": exc.detail,
            },
            status_code=exc.status_code,
        )

    @app.exception_handler(OperationError)
    def operation_error_handler(req: Request, exc: OperationError) -> JSONResponse:
        logger.error(
            msg=exc.detail,
            exc_info=exc.__cause__,
            extra={
                "extra_info": exc.extra,
                "content": str(exc.__class__.__name__),
                "path": req.url.path,
                "method": req.method,
                "service": exc.extra.get("service", "unknown"),
            },
        )
        return JSONResponse(
            content={
                "detail": exc.detail,
                "sub": exc.extra.get("sub"),
            },
            status_code=exc.status_code,
        )

    @app.exception_handler(DatabaseError)
    def database_error_handler(req: Request, exc: DatabaseError) -> JSONResponse:
        logger.error(
            msg=exc.detail,
            exc_info=exc.__cause__,
            extra={
                "extra_info": exc.extra,
                "content": str(exc.__class__.__name__),
                "path": req.url.path,
                "method": req.method,
                "service": exc.extra.get("service", "unknown"),
            },
        )
        return JSONResponse(
            content={
                "detail": exc.detail,
            },
            status_code=exc.status_code,
        )

    @app.exception_handler(BaseAppError)
    def base_app_error_handler(req: Request, exc: BaseAppError) -> JSONResponse:
        logger.error(
            msg=exc.detail,
            exc_info=exc.__cause__,
            extra={
                "extra_info": exc.extra,
                "content": str(exc.__class__.__name__),
                "path": req.url.path,
                "method": req.method,
                "service": exc.extra.get("service", "unknown"),
            },
        )
        return JSONResponse(
            content={
                "detail": exc.detail,
            },
            status_code=exc.status_code,
        )
