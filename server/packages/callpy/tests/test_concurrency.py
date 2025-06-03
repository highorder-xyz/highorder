from callpy.concurrency import BackgroundTask, BackgroundTasks
import pytest

@pytest.mark.asyncio
async def test_async_task():
    TASK_COMPLETE = False

    async def async_task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    task = BackgroundTask(async_task)

    await task()

    assert TASK_COMPLETE

@pytest.mark.asyncio
async def test_sync_task():
    TASK_COMPLETE = False

    def sync_task():
        nonlocal TASK_COMPLETE
        TASK_COMPLETE = True

    task = BackgroundTask(sync_task)

    await task()

    assert TASK_COMPLETE

@pytest.mark.asyncio
async def test_multiple_tasks():
    TASK_COUNTER = 0

    def increment(amount):
        nonlocal TASK_COUNTER
        TASK_COUNTER += amount

    tasks = BackgroundTasks()
    tasks.add_task(increment, amount=1)
    tasks.add_task(increment, amount=2)
    tasks.add_task(increment, amount=3)

    await tasks()
    assert TASK_COUNTER == 1 + 2 + 3
