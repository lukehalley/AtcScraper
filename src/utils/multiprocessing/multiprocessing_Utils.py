import os
from contextlib import closing

from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.multiprocessing.multiprocessing_Classes import MyPool

logger = getProjectLogger()

def invokePoolWithTimeout(functionToRun, functionArgs):

    timeout = int(os.getenv("MULTIPROCESSING_TIMEOUT"))

    with closing(MyPool(None)) as pool:

        functionList = []

        for functionArg in functionArgs:
            f = pool.apply_async(functionToRun, [functionArg])
            functionList.append(f)

        results = []
        for f in functionList:
            try:
                result = f.get(timeout=timeout)
                results.append(result)
            except:
                logger.info(f"TIMEOUT: {functionToRun}")
                pass

        pool.close()
        pool.terminate()

        return results