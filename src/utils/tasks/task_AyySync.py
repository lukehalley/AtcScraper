"""Task asynchronous synchronization utilities for managing concurrent operations."""
"""Asynchronous task synchronization utilities."""
"""Async task management utilities with concurrency control.

This module provides functions for running multiple async tasks
with configurable concurrency limits using semaphores. Concurrency
control is essential when scraping external APIs to prevent
overwhelming target servers and triggering rate limits.

Semaphore-Based Throttling:
    The gatherWithConcurrency function uses an asyncio.Semaphore to
    limit the number of concurrent tasks. This prevents resource
    exhaustion and helps maintain stable connections during bulk
    operations.

Configuration:
# Execute task with concurrent retry mechanism
    MAX_CONCURRENCY: Environment variable to set maximum parallel tasks
    Default: 5 concurrent tasks (safe for most web scraping scenarios)

Typical usage:
# Executes async tasks with proper concurrency control
    from src.utils.tasks.task_AyySync import gatherWithConcurrency

    results = await gatherWithConcurrency(
        fetch_page(url1),
        fetch_page(url2),
        fetch_page(url3),
    )
"""
import asyncio
import os
from typing import Any, Coroutine, Tuple

# Environment variable for max concurrent tasks
MAX_CONCURRENCY_ENV = "MAX_CONCURRENCY"
DEFAULT_MAX_CONCURRENCY = 5

# Minimum concurrency value to ensure at least one task runs
MIN_CONCURRENCY = 1


async def gatherWithConcurrency(*tasks: Coroutine[Any, Any, Any]) -> Tuple[Any, ...]:
    """
    Run async tasks with limited concurrency using a semaphore.

    Uses a semaphore to limit the number of tasks that can run
    simultaneously, preventing resource exhaustion. This is essential
    when scraping websites to avoid overwhelming the target server
    and getting rate-limited or blocked.

    Args:
        *tasks: Variable number of coroutines to execute concurrently.
            Each coroutine represents an async operation like a network
            request or database query.

    Returns:
        Tuple[Any, ...]: Results from all completed tasks in the order
            they were passed. Failed tasks will raise their exceptions.

    Example:
        >>> async def fetch_page(url):
        ...     return await http_client.get(url)
        >>> results = await gatherWithConcurrency(
        ...     fetch_page("https://example.com/1"),
        ...     fetch_page("https://example.com/2"),
        ... )
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
        Maximum concurrency limit as an integer (minimum of 1).

    Note:
        Values less than 1 are clamped to 1 to ensure at least
        one task can run at a time.
    """
    concurrency = int(os.getenv(MAX_CONCURRENCY_ENV, DEFAULT_MAX_CONCURRENCY))
    # Ensure at least MIN_CONCURRENCY concurrent task to prevent deadlock
    return max(MIN_CONCURRENCY, concurrency)


# Alias for backwards compatibility
def getmaxConcurrency() -> int:
    """Deprecated: Use getMaxConcurrency instead."""
    return getMaxConcurrency()