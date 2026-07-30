import logging
import uuid
from urllib.parse import urljoin

import httpx

from app.core.config import settings
from app.database.enums import AttemptOutcomeType
from app.schemas import ProviderCallResult

logger = logging.getLogger(__name__)


class ProviderClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=httpx.Timeout(timeout_seconds))

    async def close(self) -> None:
        await self._client.aclose()

    async def send_payment(
        self,
        operation_id: str,
        amount: str,
        currency: str,
    ) -> ProviderCallResult:
        payload = {
            "operationId": operation_id,
            "amount": amount,
            "currency": currency,
        }
        headers = {
            "Idempotency-Key": operation_id,
            "X-Correlation-ID": operation_id,
            "Content-Type": "application/json",
        }

        try:
            url = urljoin(settings.provider.url, "/payments")
            response = await self._client.post(
                url=url,
                json=payload,
                headers=headers,
            )
        except httpx.TimeoutException as e:
            logger.error("Provider call timed out", extra={"service": "provider_client", "operationId": operation_id})
            return ProviderCallResult(
                outcome=AttemptOutcomeType.TIMEOUT,
                httpStatusCode=None,
                providerPaymentId=None,
                errorDetail=str(e),
            )
        except httpx.TransportError as e:
            logger.error(
                "Provider call network error", extra={"service": "provider_client", "operationId": operation_id}
            )
            return ProviderCallResult(
                outcome=AttemptOutcomeType.NETWORK_ERROR,
                httpStatusCode=None,
                providerPaymentId=None,
                errorDetail=str(e),
            )

        if response.status_code == 503:
            return ProviderCallResult(
                outcome=AttemptOutcomeType.SERVICE_UNAVAILABLE,
                httpStatusCode=503,
                providerPaymentId=None,
                errorDetail=None,
            )

        if response.status_code == 202:
            try:
                body = response.json()
                provider_payment_id = uuid.UUID(body["providerPaymentId"])
            except Exception as e:
                logger.error(
                    "Provider returned 202 with unparsable body",
                    extra={"operationId": operation_id, "body": response.text, "service": "provider_client"},
                )
                return ProviderCallResult(
                    outcome=AttemptOutcomeType.UNEXPECTED_ERROR,
                    httpStatusCode=202,
                    providerPaymentId=None,
                    errorDetail=str(e),
                )
            return ProviderCallResult(
                outcome=AttemptOutcomeType.ACCEPTED,
                httpStatusCode=202,
                providerPaymentId=provider_payment_id,
                errorDetail=None,
            )

        logger.error(
            "Unexpected provider response",
            extra={"operationId": operation_id, "status": response.status_code, "service": "provider_client"},
        )
        return ProviderCallResult(
            outcome=AttemptOutcomeType.UNEXPECTED_ERROR,
            httpStatusCode=response.status_code,
            providerPaymentId=None,
            errorDetail=response.text[:500],
        )
