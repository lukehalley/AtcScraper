import os

from src.utils.data.data_Booleans import strToBool

def checkIsDocker():
    return strToBool(os.environ.get("RUNNING_IN_DOCKER"))

def checkHeadless():
    return checkIsDocker() or strToBool(os.getenv("FORCE_HEADLESS"))