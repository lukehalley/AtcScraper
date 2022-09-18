import os

from src.utils.data.data_Booleans import strToBool

# Check if we are running in a docker container
def checkIsDocker():
    return strToBool(os.environ.get("RUNNING_IN_DOCKER"))

# Check if we are running on AWS
def checkIsAWS():
    return True if os.environ.get("AWS_DEFAULT_REGION") else False

def checkHeadless():
    return checkIsDocker() or strToBool(os.getenv("FORCE_HEADLESS"))