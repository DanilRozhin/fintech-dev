import asyncio

import pytest

from app.database import OperationOrm
from app.database.enums import StatusType
from app.services.recovery_service import run_recovery

from .fakes import FakeProviderClient


@pytest.mark.asyncio
async def test_recovery_resumes_stuck_operation(async_client, db_session):
    fake_client = FakeProviderClient()
    async_client.app.state.provider_client = fake_client

    operation_id = "test_operation"
    operation = OperationOrm(
        operationId=operation_id,
        amount="100.00",
        currency="RUB",
        description="test operation",
        status=StatusType.PROCESSING,
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    response = await async_client.get(f"/operations/{operation_id}", follow_redirects=True)
    assert response.status_code == 200
    operation = response.json()
    assert operation.get("status", "") == "PROCESSING"

    await run_recovery(fake_client)
    await asyncio.sleep(0.1)

    events_response = await async_client.get(f"/operations/{operation_id}/events", follow_redirects=True)
    assert events_response.status_code == 200
    events = events_response.json().get("events", [])
    resumed = [e for e in events if e["type"] == "RECOVERY_RESUMED"]
    assert len(resumed) == 1
