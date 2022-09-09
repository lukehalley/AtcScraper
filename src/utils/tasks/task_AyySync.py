import asyncio
import os

# Run async task but limit how many tasks we can run at a time
async def gatherWithConcurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))

# Get the max task we can run at a time which we set
def getmaxConcurrency():
    return int(os.getenv('MAX_CONCURRENCY'))