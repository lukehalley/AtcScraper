"""
Async task management utilities with concurrency control.

This module provides functions for running multiple async tasks
with configurable concurrency limits using semaphores.
"""
import asyncio
import os
from typing import Any, Coroutine, Tuple

# Environment variable for max concurrent tasks
MAX_CONCURRENCY_ENV = "MAX_CONCURRENCY"
DEFAULT_MAX_CONCURRENCY = 5


async def gatherWithConcurrency(*tasks: Coroutine[Any, Any, Any]) -> Tuple[Any, ...]:
    """
    Run async tasks with limited concurrency.

    Uses a semaphore to limit the number of tasks that can run
    simultaneously, preventing resource exhaustion.

    Args:
        *tasks: Variable number of coroutines to execute.

    Returns:
        Tuple of results from all completed tasks.
    """
    maxConcurrency = getMaxConcurrency()
    semaphore = asyncio.Semaphore(maxConcurrency)

    async def sem_task(task: Coroutine[Any, Any, Any]) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


def getMaxConcurrency() -> int:
    """
    Get the maximum number of concurrent tasks allowed.

    Reads from the MAX_CONCURRENCY environment variable.

    Returns:
        Maximum concurrency limit as an integer.
    """
    return int(os.getenv(MAX_CONCURRENCY_ENV, DEFAULT_MAX_CONCURRENCY))


# Alias for backwards compatibility
def getmaxConcurrency() -> int:
    """Deprecated: Use getMaxConcurrency instead."""
    return getMaxConcurrency()