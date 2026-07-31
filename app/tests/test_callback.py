import asyncio
import datetime
import uuid

import pytest

from app.database.enums import CurrencyType, ReceiptResultType

from .fakes import FakeProviderClient


@pytest.mark.asyncio
async def test_receipt_before_provider_response(async_client):
    delay = 2.0
    async_client.app.state.provider_client = FakeProviderClient(delay=delay)

    operation_id = "test_operation"
    operation_request = {
        "operationId": operation_id,
        "amount": "1.00",
        "currency": CurrencyType.RUB.value,
        "description": "test operation",
    }
    response = await async_client.post("/operations", json=operation_request, follow_redirects=True)
    assert response.status_code == 201

    response = await async_client.post(
        f"/operations/{operation_id}/submit", json=operation_request, follow_redirects=True
    )
    assert response.status_code == 202

    provider_payment_id = str(uuid.uuid4())
    receipt_request = {
        "providerPaymentId": provider_payment_id,
        "operationId": operation_id,
        "result": ReceiptResultType.COMPLETED.value,
        "message": "early receipt",
        "occurredAt": str(datetime.datetime.now(datetime.timezone.utc)),
    }

    response = await async_client.post("/receipts", json=receipt_request, follow_redirects=True)
    assert response.status_code == 204

    response = await async_client.get(f"/operations/{operation_id}", follow_redirects=True)
    assert response.status_code == 200
    operation = response.json()
    assert operation.get("status", "") == "COMPLETED"
    assert operation.get("providerPaymentId", None) == provider_payment_id

    await asyncio.sleep(delay)

    events_response = await async_client.get(f"/operations/{operation_id}/events", follow_redirects=True)
    assert events_response.status_code == 200
    events = events_response.json().get("events", [])
    ignored = [e for e in events if e["type"] == "PROVIDER_LATE_RESPONSE_IGNORED"]
    assert len(ignored) == 1
