import asyncio

_background_tasks: set[asyncio.Task] = set()


def track_task(coro) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


async def wait_for_all_tasks() -> None:
    if _background_tasks:
        await asyncio.gather(*_background_tasks, return_exceptions=True)
