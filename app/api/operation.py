import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_provider_client
from app.clients import ProviderClient
from app.core.background_tasks import track_task
from app.database import db_helper
from app.database.enums import TriggerType
from app.schemas import OperationCreate, OperationEventResponse, OperationSingleResponse
from app.services import EventService, OperationService, run_provider_call_in_background

logger = logging.getLogger(__name__)

operation_router = APIRouter(
    tags=["operation"],
)


@operation_router.post("/", status_code=status.HTTP_201_CREATED, response_model=OperationSingleResponse)
async def create_operation(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    operation_request: OperationCreate,
):
    extra = {"service": "operation_post_endpoint"}
    logger.debug("Creating new operation", extra=extra)
    operation_response = await OperationService(session=session).create_operation(operation_request=operation_request)
    logger.debug("Operation created", extra=extra)
    return operation_response


@operation_router.post(
    "/{operation_id}/submit",
    response_model=OperationSingleResponse,
    responses={
        200: {"description": "Operation already submitted; current state returned"},
        202: {"description": "Submit accepted; provider call scheduled"},
        404: {"description": "Operation not found"},
    },
)
async def submit_operation(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    operation_id: str,
    provider_client: Annotated[ProviderClient, Depends(get_provider_client)],
    response: Response,
):
    extra = {"service": "operation_submit_endpoint"}
    logger.debug("Submitting operation", extra=extra)
    submit_response = await OperationService(session=session).submit_operation(operation_id=operation_id)
    if submit_response.is_submitted:
        logger.debug("Operation submitted", extra=extra)
        response.status_code = status.HTTP_202_ACCEPTED
        track_task(
            run_provider_call_in_background(
                operation_id=operation_id,
                triggered_by=TriggerType.SUBMIT,
                provider_client=provider_client,
            )
        )
        return JSONResponse(
            content=submit_response.operation.model_dump(mode="json"),
            status_code=status.HTTP_202_ACCEPTED,
        )
    logger.debug("Operation already submitted earlier", extra=extra)
    response.status_code = status.HTTP_200_OK
    return JSONResponse(
        content=submit_response.operation.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@operation_router.get(
    "/{operation_id}/events",
    response_model=OperationEventResponse,
    status_code=status.HTTP_200_OK,
)
async def get_operation_events(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    operation_id: str,
):
    extra = {"service": "events_get_endpoint"}
    logger.debug("Getting events", extra=extra)
    events = await EventService(session=session).get_operation_events(operation_id=operation_id)
    logger.debug("Events received", extra=extra)
    return events


@operation_router.get(
    "/{operation_id}",
    response_model=OperationSingleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_operation_by_id(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    operation_id: str,
):
    extra = {"service": "operation_get_endpoint"}
    logger.debug("Getting operation", extra=extra)
    operation_response = await OperationService(session=session).get_operation_by_id(operation_id=operation_id)
    logger.debug("Operation received", extra=extra)
    return operation_response
