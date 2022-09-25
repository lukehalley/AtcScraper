import json
import os

# Get an env from AWS Secret
def getAWSSecret(key):
    return json.loads(os.environ.get("ATC_DB_Credentials"))[key]