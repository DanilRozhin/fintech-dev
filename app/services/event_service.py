from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import OperationError
from app.repositories import EventRepository, OperationRepository
from app.schemas import OperationEventResponse


class EventService:
    def __init__(self, session: AsyncSession):
        self.event_repo = EventRepository(session=session)
        self.operation_repo = OperationRepository(session=session)

    async def get_operation_events(self, operation_id: str) -> OperationEventResponse:
        operation = await self.operation_repo.get_operation_by_id(operation_id=operation_id)
        if not operation:
            raise OperationError(
                detail="Operation with this ID not found",
                status_code=status.HTTP_404_NOT_FOUND,
                extra={
                    "service": "event_service",
                    "sub": operation_id,
                },
            )
        events = await self.event_repo.get_operation_events(operation_id=operation_id)
        return OperationEventResponse(events=events)
