import os

import mysql.connector
from mysql.connector import errorcode

from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def executeQuery(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()