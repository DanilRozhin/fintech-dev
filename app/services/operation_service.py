from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import StatusType
from app.exceptions import OperationError
from app.repositories import OperationRepository
from app.schemas import OperationRequest, OperationResponse


class OperationService:
    def __init__(self, session: AsyncSession):
        self.operation_repo = OperationRepository(session=session)

    async def create_operation(self, operation_request: OperationRequest) -> OperationResponse:
        operation_id = operation_request.operationId
        existing_operation = await self.operation_repo.get_operation_by_id(operation_id=operation_id)
        if existing_operation is not None:
            raise OperationError(
                detail="Operation with this ID already exists",
                status_code=status.HTTP_409_CONFLICT,
                extra={
                    "service": "operation_service",
                    "sub": operation_id,
                },
            )
        operation_response = await self.operation_repo.create_operation(
            operation_request=operation_request.model_dump()
        )
        return operation_response

    async def update_operation_status(self, operation_id: str, operation_status: StatusType) -> OperationResponse:
        operation = await self.operation_repo.update_operation_status(
            operation_id=operation_id,
            operation_status=operation_status,
        )
        if operation is not None:
            return operation
        raise OperationError(
            detail="Operation with this ID does not exist",
            status_code=status.HTTP_404_NOT_FOUND,
            extra={
                "service": "operation_service",
                "sub": operation_id,
            },
        )
