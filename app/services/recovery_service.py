import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.background_tasks import track_task
from app.database import db_helper
from app.database.enums import EventType, StatusType, TriggerType
from app.database.models import OperationEventOrm, OperationOrm
from app.services import run_provider_call_in_background

logger = logging.getLogger(__name__)


async def run_recovery(provider_client) -> None:
    async with db_helper.session_factory() as session:
        stuck_operation_ids = await _mark_and_collect_stuck_operations(session)

    logger.info("Recovery found %d stuck operations", len(stuck_operation_ids))

    for operation_id in stuck_operation_ids:
        track_task(
            run_provider_call_in_background(
                operation_id=operation_id,
                triggered_by=TriggerType.RECOVERY,
                provider_client=provider_client,
            )
        )


async def _mark_and_collect_stuck_operations(session: AsyncSession) -> list[str]:
    result = await session.execute(
        select(OperationOrm.operationId).where(OperationOrm.status == StatusType.PROCESSING)
    )
    operation_ids = list(result.scalars().all())

    for operation_id in operation_ids:
        session.add(
            OperationEventOrm(
                operationId=operation_id,
                type=EventType.RECOVERY_RESUMED,
                fromStatus=StatusType.PROCESSING,
                toStatus=StatusType.PROCESSING,
                message="Recovery resumed provider call after restart",
            )
        )

    await session.commit()
    return operation_ids
