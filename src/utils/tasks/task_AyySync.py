import asyncio
import os

# # Run async task but limit how many tasks we can run at a time
# def gatherWithConcurrency(*tasks):
#
#     # Get how many task we run in concurrently
#     maxConcurrency = getMaxConcurrency()
#
#     semaphore = asyncio.Semaphore(maxConcurrency)
#
#     def sem_task(task):
#         async with semaphore:
#             return task
#
#     return asyncio.gather(*(sem_task(task) for task in tasks))
#
# # Get the max task we can run at a time which we set
# def getMaxConcurrency():
#     return int(os.getenv('MAX_CONCURRENCY'))