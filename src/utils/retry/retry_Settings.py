import os


def getRetryParameters():
    retryAttempts = int(os.getenv("RETRY_ATTEMPTS"))
    retryDelay = int(os.getenv("RETRY_DELAY"))

    return retryAttempts, retryDelay
