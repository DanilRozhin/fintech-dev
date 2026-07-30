from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import OperationError
from app.repositories import OperationRepository
from app.schemas import OperationCreate, OperationSingleResponse, OperationSubmitResponse


class OperationService:
    def __init__(self, session: AsyncSession):
        self._operation_repo = OperationRepository(session=session)

    async def create_operation(self, operation_request: OperationCreate) -> OperationSingleResponse:
        operation_response = await self._operation_repo.create_operation(operation_request=operation_request)
        if operation_response is None:
            raise OperationError(
                detail="Operation with this ID already exists",
                status_code=status.HTTP_409_CONFLICT,
                extra={
                    "service": "operation_service",
                    "sub": operation_request.operationId,
                },
            )
        return operation_response

    async def get_operation_by_id(self, operation_id: str) -> OperationSingleResponse:
        operation = await self._operation_repo.get_operation_by_id(operation_id=operation_id)
        if operation is None:
            raise OperationError(
                detail="Operation with this ID not found",
                status_code=status.HTTP_404_NOT_FOUND,
                extra={
                    "service": "operation_service",
                    "sub": operation_id,
                },
            )
        return operation

    async def submit_operation(self, operation_id: str) -> OperationSubmitResponse:
        response = await self._operation_repo.submit_operation(operation_id=operation_id)
        if response.operation is None:
            raise OperationError(
                detail="Operation with this ID not found",
                status_code=status.HTTP_404_NOT_FOUND,
                extra={
                    "service": "operation_service",
                    "sub": operation_id,
                },
            )
        return response
