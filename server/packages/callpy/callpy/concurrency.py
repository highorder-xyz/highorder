import asyncio
import functools
import typing
from typing import Any, AsyncGenerator, Iterator

try:
    import contextvars  # Python 3.7+ only.
except ImportError:  # pragma: no cover
    contextvars = None  # type: ignore

T = typing.TypeVar("T")


async def run_until_first_complete(*args: typing.Tuple[typing.Callable, dict]) -> None:
    tasks = [handler(**kwargs) for handler, kwargs in args]
    (done, pending) = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    [task.cancel() for task in pending]
    [task.result() for task in done]


async def run_in_threadpool(
    func: typing.Callable[..., T], *args: typing.Any, **kwargs: typing.Any
) -> T:
    loop = asyncio.get_event_loop()
    if contextvars is not None:  # pragma: no cover
        # Ensure we run in the same context
        child = functools.partial(func, *args, **kwargs)
        context = contextvars.copy_context()
        func = context.run
        args = (child,)
    elif kwargs:  # pragma: no cover
        # loop.run_in_executor doesn't accept 'kwargs', so bind them in here
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)


class _StopIteration(Exception):
    pass


def _next(iterator: Iterator) -> Any:
    # We can't raise `StopIteration` from within the threadpool iterator
    # and catch it outside that context, so we coerce them into a different
    # exception type.
    try:
        return next(iterator)
    except StopIteration:
        raise _StopIteration


async def iterate_in_threadpool(iterator: Iterator) -> AsyncGenerator:
    while True:
        try:
            yield await run_in_threadpool(_next, iterator)
        except _StopIteration:
            break


class BackgroundTask:
    def __init__(
        self, func: typing.Callable, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_async = asyncio.iscoroutinefunction(func)

    async def __call__(self) -> None:
        if self.is_async:
            await self.func(*self.args, **self.kwargs)
        else:
            await run_in_threadpool(self.func, *self.args, **self.kwargs)


class BackgroundTasks(BackgroundTask):
    def __init__(self, tasks: typing.Sequence[BackgroundTask] = []):
        self.tasks = list(tasks)

    def add_task(
        self, func: typing.Callable, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        task = BackgroundTask(func, *args, **kwargs)
        self.tasks.append(task)

    async def __call__(self) -> None:
        for task in self.tasks:
            await task()