import os

from src.utils.data.data_Booleans import strToBool

def checkIsLazyMode():
    return strToBool(os.getenv("LAZY_MODE"))