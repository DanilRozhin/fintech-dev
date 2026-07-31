import asyncio

import pytest

from app.database.enums import CurrencyType


@pytest.mark.asyncio
async def test_concurrent_submit_creates_single_transition(async_client):
    operation_id = "test_operation"
    operation_request = {
        "operationId": operation_id,
        "amount": "1.00",
        "currency": CurrencyType.RUB.value,
        "description": "test operation",
    }
    response = await async_client.post("/operations", json=operation_request, follow_redirects=True)
    assert response.status_code == 201
    data = response.json()
    assert data["operationId"] == operation_id

    responses = await asyncio.gather(
        *[async_client.post(f"/operations/{operation_id}/submit", follow_redirects=True) for _ in range(10)],
        return_exceptions=True,
    )

    status_codes = [r.status_code for r in responses]
    assert status_codes.count(202) == 1
    assert status_codes.count(200) == 9

    events_response = await async_client.get(f"/operations/{operation_id}/events", follow_redirects=True)
    assert events_response.status_code == 200
    events = events_response.json().get("events", [])
    submit_accepted = [e for e in events if e["type"] == "SUBMIT_ACCEPTED"]
    submit_duplicate_ignored = [e for e in events if e["type"] == "SUBMIT_DUPLICATE_IGNORED"]
    assert len(submit_accepted) == 1
    assert len(submit_duplicate_ignored) == 9
