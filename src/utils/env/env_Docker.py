import os

# Check if we are running in a docker container
def checkIsDocker():
    return True if os.environ.get("AWS_DEFAULT_REGION") else False