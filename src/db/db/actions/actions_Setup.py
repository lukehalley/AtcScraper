import os

import mysql.connector
from mysql.connector import errorcode

from src.utils.env.env_AWSSecrets import getAWSSecret
from src.utils.logging.logging_Setup import getProjectLogger, printLog

logger = getProjectLogger()

def initDBConnection():

    DB_USER = getAWSSecret("username")
    DB_PASSWORD = getAWSSecret("password")
    DB_ENDPOINT = os.getenv("DB_ENDPOINT")
    DB_NAME = os.getenv("DB_NAME")

    try:
        dbConnection = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_ENDPOINT,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        printLog("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        printLog("Database does not exist")
      else:
        printLog(err)
    else:
        return dbConnection

def getCursor(dbConnection, dictionary=True, buffered=True):
    return dbConnection.cursor(dictionary=dictionary, buffered=buffered)