from datetime import datetime
import os
from time import strftime, gmtime


# Get current date time
def getCurrentDateTime():
    return datetime.now().strftime(os.environ.get("DATE_FORMAT"))


# Get time in min and sec format
def getMinSecString(time):
    timFormat = os.getenv("TIMER_STR_FORMAT")
    return strftime(timFormat, gmtime(time))
