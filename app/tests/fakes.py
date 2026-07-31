import asyncio
import uuid

from app.database.enums import AttemptOutcomeType
from app.schemas import ProviderCallResult


class FakeProviderClient:
    def __init__(self, outcome: AttemptOutcomeType = AttemptOutcomeType.ACCEPTED, delay: float = 0.0):
        self.outcome = outcome
        self.call_count = 0
        self.delay = delay

    async def send_payment(self, operation_id: str, amount: str, currency: str) -> ProviderCallResult:
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        self.call_count += 1
        if self.outcome == AttemptOutcomeType.ACCEPTED:
            return ProviderCallResult(
                outcome=AttemptOutcomeType.ACCEPTED,
                httpStatusCode=202,
                providerPaymentId=uuid.uuid4(),
                errorDetail=None,
            )
        return ProviderCallResult(
            outcome=self.outcome,
            httpStatusCode=503,
            providerPaymentId=None,
            errorDetail="simulated failure",
        )
