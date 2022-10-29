import os
from pathlib import Path

import boto3

def downloadAbisFromS3():

    s3 = boto3.resource('s3')
    bucket = s3.Bucket('atc-abis')

    key = 'mapped-abis/'
    files = list(bucket.objects.filter(Prefix=key))

    downloadDir = "data"

    for file in files:

        folderPath = file.key.split('/')[:-1]
        fileName = file.key.split('/')[-1]
        fileExtension = os.path.splitext(fileName)[-1]

        if fileExtension.lower() == ".json":

            localPath = f"{downloadDir}/{os.path.join(*folderPath)}"
            downloadDestination = f"{localPath}/{fileName}"

            if not os.path.isfile(downloadDestination):
                Path(localPath).mkdir(parents=True, exist_ok=True)
                bucket.download_file(file.key, downloadDestination)