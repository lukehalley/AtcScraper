import asyncio
import os


async def gatherWithConcurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))

def getmaxConcurrency():
    return int(os.getenv('MAX_CONCURRENCY'))