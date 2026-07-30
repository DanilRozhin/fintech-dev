import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_helper
from app.schemas import ReceiptRequest
from app.services import ReceiptService

logger = logging.getLogger(__name__)

receipt_router = APIRouter(
    tags=["receipt"],
)


@receipt_router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def post_receipt(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    receipt_request: ReceiptRequest,
):
    extra = {"service": "receipt_post_endpoint"}
    logger.debug("Posting receipt request", extra=extra)
    await ReceiptService(session=session).post_receipt(receipt_request=receipt_request)
    logger.debug("Receipt record made", extra=extra)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
