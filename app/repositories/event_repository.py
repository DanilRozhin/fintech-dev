import logging

from pydantic import ValidationError
from sqlalchemy import asc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import OperationEventOrm
from app.exceptions import BaseAppError, DatabaseError, ValidationObjectError
from app.schemas import OperationEventSingle

logger = logging.getLogger(__name__)


class EventRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_operation_events(self, operation_id: str) -> list[OperationEventSingle]:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Getting events", extra=extra)

        try:
            query = (
                select(OperationEventOrm)
                .where(OperationEventOrm.operationId == operation_id)
                .order_by(asc(OperationEventOrm.eventId))
            )
            res = await self._session.execute(query)
            events = res.scalars().all()
            if not events:
                return []
            return [OperationEventSingle.model_validate(event) for event in events]

        except SQLAlchemyError as e:
            extra.update(original_error=str(e))
            raise DatabaseError(
                detail="Failed to get events",
                extra=extra,
            ) from e

        except ValidationError as e:
            await self._session.rollback()
            extra.update(original_error=str(e))
            raise ValidationObjectError(
                detail="Failed to validate object before returning",
                extra=extra,
            ) from e

        except Exception as e:
            extra.update(original_error=str(e))
            raise BaseAppError(
                detail="Unexpected error while getting events",
                extra=extra,
            ) from e
