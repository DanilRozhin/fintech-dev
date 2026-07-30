import datetime
import logging

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import AttemptOutcomeType, EventType, StatusType, TriggerType
from app.database.models import OperationEventOrm, OperationOrm, ProviderAttemptOrm
from app.schemas import ProviderCallResult

logger = logging.getLogger(__name__)


class ProviderAttemptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_attempt_and_apply_result(
        self,
        operation_id: str,
        attempt_number: int,
        triggered_by: TriggerType,
        requested_at: datetime.datetime,
        result: ProviderCallResult,
    ) -> None:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Recording attempt and applying result", extra=extra)

        try:
            operation = await self._session.get(
                OperationOrm,
                operation_id,
                with_for_update=True,
            )
            if operation is None:
                # operation suddenly disappeared
                logger.error(
                    "Operation not found while attempting to apply result",
                    extra=extra,
                )
                return

            self._session.add(
                ProviderAttemptOrm(
                    operationId=operation_id,
                    attemptNumber=attempt_number,
                    requestedAt=requested_at,
                    triggeredBy=triggered_by,
                    outcome=result.outcome,
                    httpStatusCode=result.httpStatusCode,
                )
            )

            if result.outcome != AttemptOutcomeType.ACCEPTED:
                await self._session.commit()
                return

            if operation.status in (StatusType.COMPLETED, StatusType.REJECTED):
                self._session.add(
                    OperationEventOrm(
                        operationId=operation_id,
                        type=EventType.PROVIDER_LATE_RESPONSE_IGNORED,
                        fromStatus=operation.status,
                        toStatus=operation.status,
                        message=f"Late 202 ignored, operation already {operation.status.value}",
                    )
                )
                await self._session.commit()
                return

            if operation.providerPaymentId is None:
                operation.providerPaymentId = result.providerPaymentId
                self._session.add(
                    OperationEventOrm(
                        operationId=operation_id,
                        type=EventType.PROVIDER_PAYMENT_ID_ASSIGNED,
                        fromStatus=operation.status,
                        toStatus=operation.status,
                        message=f"providerPaymentId={result.providerPaymentId} assigned from provider response",
                    )
                )

            await self._session.commit()

        except SQLAlchemyError as e:
            await self._session.rollback()
            extra.update(original_error=str(e), content=str(e.__class__.__name__))
            logger.error(
                "Unexpected database error while operation for provider call",
                exc_info=e.__cause__,
                extra=extra,
            )
            return

        except ValidationError as e:
            await self._session.rollback()
            extra.update(original_error=str(e), content=str(e.__class__.__name__))
            logger.error(
                "Validation error while getting operation for provider call",
                exc_info=e.__cause__,
                extra=extra,
            )
            return

        except Exception as e:
            await self._session.rollback()
            extra.update(original_error=str(e), content=str(e.__class__.__name__))
            logger.error(
                "Something wrong occurred while getting operation for provider call",
                exc_info=e.__cause__,
                extra=extra,
            )
            return
