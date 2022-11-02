import logging
import os
import sys, time


# Setup logger
def setupLogging():
    logger = logging.getLogger("DFK-ARB")

    log_format = '%(asctime)s | %(levelname)s | %(message)s'
    dateFormat = os.environ.get("DATE_FORMAT")

    logging.basicConfig(level=logging.INFO, format=log_format,
                        stream=sys.stdout, datefmt=dateFormat)

    return logger

def printLog(msg):

    t = time.localtime()
    ascTime = time.asctime(t)

    print(f'{ascTime} | PINFO | {msg}')

# Get the project logger
def getProjectLogger():
    return logging.getLogger("DFK-DEX")
