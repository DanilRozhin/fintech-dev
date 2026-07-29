import logging

from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import EventType, StatusType
from app.database.models import OperationEventOrm, OperationOrm
from app.exceptions import BaseAppError, DatabaseError, ValidationObjectError
from app.schemas import OperationCreate, OperationSingleResponse, OperationSubmitResponse

logger = logging.getLogger(__name__)


class OperationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_operation(self, operation_request: OperationCreate) -> OperationSingleResponse | None:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Creating new operation", extra=extra)

        try:
            operation = OperationOrm(
                operationId=operation_request.operationId,
                amount=operation_request.amount,
                currency=operation_request.currency,
                description=operation_request.description,
                status=StatusType.CREATED,
            )
            self.session.add(operation)

            try:
                await self.session.flush()

            except IntegrityError:
                await self.session.rollback()
                return None

            event = OperationEventOrm(
                operationId=operation.operationId,
                type=EventType.CREATED,
                fromStatus=None,
                toStatus=StatusType.CREATED,
                message="Operation created",
            )
            self.session.add(event)
            operation_response = OperationSingleResponse.model_validate(operation)

        except SQLAlchemyError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise DatabaseError(
                detail="Failed to create new operation",
                extra=extra,
            ) from e

        except ValidationError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise ValidationObjectError(
                detail="Failed to validate object before returning",
                extra=extra,
            ) from e

        except Exception as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise BaseAppError(
                detail="Unexpected error while creating new operation",
                extra=extra,
            ) from e

        await self.session.commit()
        return operation_response

    async def get_operation_by_id(self, operation_id: str) -> OperationSingleResponse | None:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Getting operation by id", extra=extra)

        try:
            operation = await self.session.get(OperationOrm, operation_id)
            if operation is not None:
                return OperationSingleResponse.model_validate(operation)
            return None

        except SQLAlchemyError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise DatabaseError(
                detail="Failed to get operation by id",
                extra=extra,
            ) from e

        except ValidationError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise ValidationObjectError(
                detail="Failed to validate object before returning",
                extra=extra,
            ) from e

        except Exception as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise BaseAppError(
                detail="Unexpected error while getting operation by id",
                extra=extra,
            ) from e

    async def submit_operation(self, operation_id: str) -> OperationSubmitResponse:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Submitting operation", extra=extra)

        try:
            stmt = (
                update(OperationOrm)
                .where(
                    OperationOrm.operationId == operation_id,
                    OperationOrm.status == StatusType.CREATED,
                )
                .values(status=StatusType.PROCESSING)
                .returning(OperationOrm)
            )
            result = await self.session.execute(stmt)
            updated_operation = result.scalar_one_or_none()

            if updated_operation is not None:
                event = OperationEventOrm(
                    operationId=operation_id,
                    type=EventType.SUBMIT_ACCEPTED,
                    fromStatus=StatusType.CREATED,
                    toStatus=StatusType.PROCESSING,
                    message="Submit accepted, provider call scheduled",
                )
                self.session.add(event)
                operation_response = OperationSingleResponse.model_validate(updated_operation)
                is_submitted_response = True

            else:
                query = select(OperationOrm).where(OperationOrm.operationId == operation_id)
                res = await self.session.execute(query)
                operation = res.scalar_one_or_none()
                if operation is None:
                    return OperationSubmitResponse(
                        operation=None,
                        is_submitted=False,
                    )

                event = OperationEventOrm(
                    operationId=operation_id,
                    type=EventType.SUBMIT_DUPLICATE_IGNORED,
                    fromStatus=operation.status,
                    toStatus=operation.status,
                    message="Duplicate submit ignored",
                )
                self.session.add(event)
                operation_response = OperationSingleResponse.model_validate(operation)
                is_submitted_response = False

            operation_submit_response = OperationSubmitResponse(
                operation=operation_response,
                is_submitted=is_submitted_response,
            )

        except SQLAlchemyError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise DatabaseError(
                detail="Failed to submit operation",
                extra=extra,
            ) from e

        except ValidationError as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise ValidationObjectError(
                detail="Failed to validate object before returning",
                extra=extra,
            ) from e

        except Exception as e:
            await self.session.rollback()
            extra.update(original_error=str(e))
            raise BaseAppError(
                detail="Unexpected error while submitting operation",
                extra=extra,
            ) from e

        await self.session.commit()
        return operation_submit_response
