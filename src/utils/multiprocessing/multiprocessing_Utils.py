import os
from contextlib import closing

from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.multiprocessing.multiprocessing_Classes import MyPool

logger = getProjectLogger()

def invokePoolWithTimeout(functionToRun, functionArgs):

    timeout = int(os.getenv("MULTIPROCESSING_TIMEOUT_SECS"))
    timeoutLimit = int(os.getenv("MULTIPROCESSING_TIMEOUT_LIMIT"))
    with closing(MyPool(None)) as pool:

        functionList = []

        for functionArg in functionArgs:
            f = pool.apply_async(functionToRun, [functionArg])
            functionList.append(f)

        results = []
        timeoutCounter = 0
        for f in functionList:
            try:
                result = f.get(timeout=timeout)
                results.append(result)
            except:
                timeoutCounter = timeoutCounter + 1
                if timeoutCounter < timeoutLimit:
                    if timeoutCounter <= 1:
                        logger.info(f"TIMEOUT: {functionToRun}")
                    pass
                else:
                    logger.info(f"TIMEOUT LIMIT REACHED FOR: {functionToRun}")
                    break

        pool.close()
        pool.terminate()

        return results