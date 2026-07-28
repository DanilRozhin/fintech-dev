import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_helper
from app.schemas import OperationRequest, OperationSingle
from app.services import OperationService

logger = logging.getLogger(__name__)

operation_router = APIRouter(
    tags=["operation"],
)


@operation_router.post("/", status_code=status.HTTP_201_CREATED, response_model=OperationSingle)
async def create_operation(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    operation_request: OperationRequest,
):
    extra = {"service": "operation_post_endpoint"}
    logger.debug("Creating new operation", extra=extra)
    operation_response = await OperationService(session=session).create_operation(operation_request=operation_request)
    logger.debug("Operation created", extra=extra)
    return operation_response


@operation_router.get(
    "/{operation_id}",
    response_model=OperationSingle,
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
