import asyncio
import datetime
import logging
import random

from app.clients.provider_client import ProviderClient
from app.core.config import settings
from app.database import db_helper
from app.database.enums import AttemptOutcomeType, TriggerType
from app.repositories import OperationRepository, ProviderAttemptRepository

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = settings.provider.max_attempts
BASE_DELAY_SECONDS = settings.provider.base_delay_seconds
MAX_DELAY_SECONDS = settings.provider.max_delay_seconds
JITTER_SECONDS = settings.provider.jitter_seconds

RETRIABLE_OUTCOMES = {
    AttemptOutcomeType.SERVICE_UNAVAILABLE,
    AttemptOutcomeType.NETWORK_ERROR,
    AttemptOutcomeType.TIMEOUT,
    AttemptOutcomeType.UNEXPECTED_ERROR,
}


async def run_provider_call_in_background(
    operation_id: str,
    triggered_by: TriggerType,
    provider_client: ProviderClient,
) -> None:
    async with db_helper.session_factory() as session:
        service = ProviderCallService(
            provider_client=provider_client,
            operation_repository=OperationRepository(session),
            provider_attempt_repository=ProviderAttemptRepository(session),
        )
        await service.call_provider_with_retry(operation_id, triggered_by)


class ProviderCallService:
    def __init__(
        self,
        provider_client: ProviderClient,
        operation_repository: OperationRepository,
        provider_attempt_repository: ProviderAttemptRepository,
    ) -> None:
        self._provider_client = provider_client
        self._operation_repository = operation_repository
        self._provider_attempt_repository = provider_attempt_repository

    async def call_provider_with_retry(
        self,
        operation_id: str,
        triggered_by: TriggerType,
    ) -> None:
        operation = await self._operation_repository.get_for_provider_call(operation_id)
        if operation is None:
            logger.error(
                "Failed to get operation before provider call",
                extra={"operationId": operation_id, "service": "provider_call_service"},
            )
            return

        amount_str = str(operation.amount)
        currency = operation.currency.value

        for attempt_number in range(1, MAX_ATTEMPTS + 1):
            requested_at = datetime.datetime.now(datetime.timezone.utc)

            result = await self._provider_client.send_payment(
                operation_id=operation_id,
                amount=amount_str,
                currency=currency,
            )

            await self._provider_attempt_repository.record_attempt_and_apply_result(
                operation_id=operation_id,
                attempt_number=attempt_number,
                triggered_by=triggered_by,
                requested_at=requested_at,
                result=result,
            )

            if result.outcome == AttemptOutcomeType.ACCEPTED:
                return

            if result.outcome not in RETRIABLE_OUTCOMES:
                return

            if attempt_number == MAX_ATTEMPTS:
                logger.error(
                    "Provider call retries exhausted, operation stays PROCESSING",
                    extra={
                        "operationId": operation_id,
                        "attempts": attempt_number,
                        "service": "provider_call_service",
                    },
                )
                return

            delay = min(BASE_DELAY_SECONDS * (2 ** (attempt_number - 1)), MAX_DELAY_SECONDS)
            delay += random.uniform(0, JITTER_SECONDS)
            await asyncio.sleep(delay)
