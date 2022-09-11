import os

import mysql.connector
from mysql.connector import errorcode

from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def initDBConnection():

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_ENDPOINT = os.getenv("DB_ENDPOINT")
    DB_NAME = os.getenv("DB_NAME")

    try:
        cnx = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_ENDPOINT,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    else:
        return cnx

def getCursor(cnx, dictionary=True, buffered=True):
    return cnx.cursor(dictionary=dictionary, buffered=buffered)