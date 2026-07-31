import datetime
import uuid

import pytest

from app.database.enums import CurrencyType, ReceiptResultType

from .fakes import FakeProviderClient


@pytest.mark.asyncio
async def test_duplicate_and_conflicting_receipts(async_client):
    async_client.app.state.provider_client = FakeProviderClient(delay=0.0)

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

    mismatched_provider_payment_id = str(uuid.uuid4())
    receipt_request_mismatched_payment_id = {
        "providerPaymentId": mismatched_provider_payment_id,
        "operationId": operation_id,
        "result": ReceiptResultType.COMPLETED.value,
        "message": "receipt",
        "occurredAt": str(datetime.datetime.now(datetime.timezone.utc)),
    }

    response = await async_client.post("/receipts", json=receipt_request_mismatched_payment_id, follow_redirects=True)
    assert response.status_code == 409

    response = await async_client.get(f"/operations/{operation_id}", follow_redirects=True)
    assert response.status_code == 200
    operation = response.json()
    assert operation.get("status", "") == "PROCESSING"
    assert operation.get("providerPaymentId", None) != mismatched_provider_payment_id

    events_response = await async_client.get(f"/operations/{operation_id}/events", follow_redirects=True)
    assert events_response.status_code == 200
    events = events_response.json().get("events", [])

    assigned = [e for e in events if e["type"] == "PROVIDER_PAYMENT_ID_ASSIGNED"]
    assert len(assigned) == 1

    mismatched = [e for e in events if e["type"] == "RECEIPT_PAYMENT_ID_MISMATCH"]
    assert len(mismatched) == 1
