import logging

from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import StatusType
from app.database.models import OperationOrm
from app.exceptions import BaseAppError, DatabaseError
from app.schemas import OperationSingle

logger = logging.getLogger(__name__)


class OperationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_operation(self, operation_request: dict) -> OperationSingle:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Creating new operation", extra=extra)

        try:
            stmt = insert(OperationOrm).values(**operation_request).returning(OperationOrm)
            res = await self.session.execute(stmt)
            await self.session.commit()
            operation = res.scalar_one()
            return OperationSingle.model_validate(operation)

        except SQLAlchemyError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise DatabaseError(
                detail="Failed to create new operation",
                extra=extra,
            ) from e

        except Exception as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise BaseAppError(
                detail="Unexpected error while creating new operation",
                extra=extra,
            ) from e

    async def get_operation_by_id(self, operation_id: str) -> OperationSingle | None:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Getting operation by id", extra=extra)

        try:
            operation = await self.session.get(OperationOrm, operation_id)
            if operation is not None:
                return OperationSingle.model_validate(operation)
            return None

        except SQLAlchemyError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise DatabaseError(
                detail="Failed to get operation by id",
                extra=extra,
            ) from e

        except Exception as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise BaseAppError(
                detail="Unexpected error while getting operation by id",
                extra=extra,
            ) from e

    async def update_operation_status(self, operation_id: str, operation_status: StatusType) -> OperationSingle | None:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Updating operation status", extra=extra)

        try:
            operation = await self.session.get(OperationOrm, operation_id)
            if operation is None:
                return None
            operation.status = operation_status
            await self.session.commit()
            await self.session.refresh(operation)
            return OperationSingle.model_validate(operation)

        except SQLAlchemyError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise DatabaseError(
                detail="Failed to get operation by id",
                extra=extra,
            ) from e

        except Exception as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise BaseAppError(
                detail="Unexpected error while getting operation by id",
                extra=extra,
            ) from e
