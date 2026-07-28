import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_helper
from app.schemas import OperationEventResponse
from app.services import EventService

logger = logging.getLogger(__name__)

event_router = APIRouter(
    tags=["event"],
)


@event_router.get(
    "/events",
    response_model=OperationEventResponse,
    status_code=status.HTTP_200_OK,
)
async def get_operation_events(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    operation_id: str,
):
    extra = {"service": "events_get_endpoint"}
    logger.debug("Getting events", extra=extra)
    events = await EventService(session=session).get_operation_events(operation_id=operation_id)
    logger.debug("Events received", extra=extra)
    return events
