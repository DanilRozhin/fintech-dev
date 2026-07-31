from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.enums import ReceiptOutcome
from app.exceptions import OperationError, ProviderPaymentIdMismatchError
from app.repositories import ReceiptRepository
from app.schemas import ReceiptRequest


class ReceiptService:
    def __init__(self, session: AsyncSession):
        self._receipt_repo = ReceiptRepository(session=session)

    async def post_receipt(self, receipt_request: ReceiptRequest) -> ReceiptOutcome:
        response = await self._receipt_repo.post_receipt(receipt_request=receipt_request)
        if response is None:
            raise OperationError(
                detail="Operation with this ID not found",
                status_code=status.HTTP_404_NOT_FOUND,
                extra={
                    "service": "operation_service",
                    "sub": receipt_request.operationId,
                },
            )
        if response == ReceiptOutcome.MISMATCH:
            raise ProviderPaymentIdMismatchError(
                detail="Provider Payment ID mismatch",
                status_code=status.HTTP_409_CONFLICT,
                extra={
                    "service": "receipt_service",
                    "provider_payment_id": str(receipt_request.providerPaymentId),
                    "operation_id": receipt_request.operationId,
                },
            )
        return response
