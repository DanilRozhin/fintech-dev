import asyncio
import logging

logger = logging.getLogger(__name__)

_background_tasks: set[asyncio.Task] = set()


def track_task(coro) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


async def wait_for_all_tasks(timeout: float = 20.0) -> None:
    if not _background_tasks:
        return
    logger.info("Waiting for %d background tasks to finish", len(_background_tasks))
    _done, pending = await asyncio.wait(_background_tasks, timeout=timeout)
    if pending:
        logger.warning("%d background tasks did not finish in time, cancelling", len(pending))
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
