import logging
import os
import sys, time
from datetime import datetime

# Setup logger
def setupLogging():
    logger = logging.getLogger("DFK-ARB")

    log_format = '%(asctime)s | %(levelname)s | %(message)s'
    dateFormat = os.environ.get("DATE_FORMAT")

    logging.basicConfig(level=logging.INFO, format=log_format,
                        stream=sys.stdout, datefmt=dateFormat)

    return logger

def printLog(msg):
    now = datetime.now()
    dateFormat = "%Y-%m-%d %H:%M:%S,%f"
    timeStr = now.strftime(dateFormat)[:-3]
    print(f'{timeStr} | PNFO | {msg}')

# Get the project logger
def getProjectLogger():
    return logging.getLogger("DFK-DEX")
