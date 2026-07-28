from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import OperationError
from app.repositories import EventRepository
from app.schemas import OperationEventResponse


class EventService:
    def __init__(self, session: AsyncSession):
        self.event_repo = EventRepository(session=session)

    async def get_operation_events(self, operation_id: str) -> OperationEventResponse:
        events = await self.event_repo.get_operation_events(operation_id=operation_id)
        if not events:
            raise OperationError(
                detail="Operation with this ID not found",
                status_code=status.HTTP_404_NOT_FOUND,
                extra={
                    "service": "event_service",
                    "sub": operation_id,
                },
            )
        return OperationEventResponse(events=events)
