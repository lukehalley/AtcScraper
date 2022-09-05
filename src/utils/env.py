# Check if we are running in a docker container
import os

def checkIsDocker():
    return True if os.environ.get("AWS_DEFAULT_REGION") else False