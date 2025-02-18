from datetime import datetime
import os
from time import strftime, gmtime
from typing import Optional


def getCurrentDateTime() -> str:
    """Get current date time formatted according to DATE_FORMAT env variable."""
    return datetime.now().strftime(os.environ.get("DATE_FORMAT", "%Y-%m-%d %H:%M:%S"))


def getMinSecString(time: float) -> str:
    """Get time in minutes and seconds format."""
    timFormat = os.getenv("TIMER_STR_FORMAT", "%M:%S")
    return strftime(timFormat, gmtime(time))
