from typing import Any

from fastapi import status


class BaseAppError(Exception):
    """Base exception for all exceptions in the app"""

    def __init__(
        self,
        detail: str = "Unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        extra: dict[str, Any] | None = None,
    ):
        self.detail = detail
        self.extra = extra or {}
        self.status_code = status_code
        super().__init__(detail)


class OperationError(BaseAppError):
    """Raised when an exception related to an operation occurs"""

    def __init__(
        self,
        detail: str = "Operation failed",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        extra: dict[str, Any] | None = None,
    ):
        super().__init__(detail=detail, status_code=status_code, extra=extra)


class DatabaseError(BaseAppError):
    """Database related error"""

    def __init__(
        self,
        detail: str = "Database error occurred",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        extra: dict[str, Any] | None = None,
    ):
        super().__init__(detail=detail, status_code=status_code, extra=extra)


class ValidationObjectError(BaseAppError):
    """Validation object related error"""

    def __init__(
        self,
        detail: str = "Validation object error occurred",
        status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT,
        extra: dict[str, Any] | None = None,
    ):
        super().__init__(detail=detail, status_code=status_code, extra=extra)


class ProviderPaymentIdMismatchError(BaseAppError):
    """Provider payment id mismatch error"""

    def __init__(
        self,
        detail: str = "Provider Payment ID mismatch error",
        status_code: int = status.HTTP_409_CONFLICT,
        extra: dict[str, Any] | None = None,
    ):
        super().__init__(detail=detail, status_code=status_code, extra=extra)
