import logging

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import EventType, ReceiptOutcome, ReceiptResultType, StatusType
from app.database.models import OperationEventOrm, OperationOrm, ReceiptRecordOrm
from app.exceptions import BaseAppError, DatabaseError, ValidationObjectError
from app.schemas import ReceiptRequest

logger = logging.getLogger(__name__)


class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def post_receipt(self, receipt_request: ReceiptRequest) -> ReceiptOutcome | None:
        service_name = str(self.__class__.__name__)
        extra = {"service": service_name}
        logger.debug("Posting receipt", extra=extra)

        try:
            query = (
                select(OperationOrm).where(OperationOrm.operationId == receipt_request.operationId).with_for_update()
            )
            res = await self.session.execute(query)
            operation = res.scalar_one_or_none()

            if operation is None:
                return None

            incoming_status_final = (
                StatusType.COMPLETED
                if receipt_request.result == ReceiptResultType.COMPLETED
                else ReceiptResultType.REJECTED
            )

            # provider payment id mismatch
            if (
                operation.providerPaymentId is not None
                and operation.providerPaymentId != receipt_request.providerPaymentId
            ):
                try:
                    event = OperationEventOrm(
                        operationId=operation.operationId,
                        type=EventType.RECEIPT_PAYMENT_ID_MISMATCH,
                        fromStatus=operation.status,
                        toStatus=operation.status,
                        message=f"Mismatched provider payment ID={receipt_request.providerPaymentId}",
                    )
                    self.session.add(event)
                    await self.session.flush()
                    receipt_record = ReceiptRecordOrm(
                        operationId=operation.operationId,
                        providerPaymentId=receipt_request.providerPaymentId,
                        result=receipt_request.result,
                        message=receipt_request.message,
                        occurredAt=receipt_request.occurredAt,
                        eventId=event.eventId,
                    )
                    self.session.add(receipt_record)

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
                return ReceiptOutcome.MISMATCH  # 409

            # operation already finished
            if operation.status in (StatusType.COMPLETED, StatusType.REJECTED):
                try:
                    is_duplicate = operation.status == incoming_status_final
                    event_type = (
                        EventType.RECEIPT_DUPLICATE_IGNORED if is_duplicate else EventType.RECEIPT_CONFLICT_IGNORED
                    )
                    event = OperationEventOrm(
                        operationId=operation.operationId,
                        type=event_type,
                        fromStatus=operation.status,
                        toStatus=operation.status,
                        message=f"Receipt result={receipt_request.result} while operation already {operation.status}",
                    )
                    self.session.add(event)
                    await self.session.flush()
                    receipt_record = ReceiptRecordOrm(
                        operationId=operation.operationId,
                        providerPaymentId=receipt_request.providerPaymentId,
                        result=receipt_request.result,
                        message=receipt_request.message,
                        occurredAt=receipt_request.occurredAt,
                        eventId=event.eventId,
                    )
                    self.session.add(receipt_record)

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
                return ReceiptOutcome.IGNORED  # 204

            # applying receipt
            events_to_add = []
            if operation.providerPaymentId is None:
                operation.providerPaymentId = receipt_request.providerPaymentId
                assigned_event = OperationEventOrm(
                    operationId=operation.operationId,
                    type=EventType.PROVIDER_PAYMENT_ID_ASSIGNED,
                    fromStatus=operation.status,
                    toStatus=operation.status,
                    message="Provider payment ID assigned from receipt",
                )
                events_to_add.append(assigned_event)

            from_status = operation.status
            operation.status = incoming_status_final
            apply_event = OperationEventOrm(
                operationId=operation.operationId,
                type=EventType.RECEIPT_APPLIED,
                fromStatus=from_status,
                toStatus=incoming_status_final,
                message=f"Receipt applied: {receipt_request.result}",
            )
            events_to_add.append(apply_event)

            self.session.add_all(events_to_add)
            await self.session.flush()

            receipt_record = ReceiptRecordOrm(
                operationId=operation.operationId,
                providerPaymentId=receipt_request.providerPaymentId,
                result=receipt_request.result,
                message=receipt_request.message,
                occurredAt=receipt_request.occurredAt,
                eventId=apply_event.eventId,
            )
            self.session.add(receipt_record)

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
        return ReceiptOutcome.APPLIED  # 204
