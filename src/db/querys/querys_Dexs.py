from functools import lru_cache

from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

@lru_cache()
def getAllDexsForNetwork(networkDbId):

    query = "" \
            f"SELECT name " \
            f"FROM dexs " \
            f"WHERE network_id={networkDbId}"

    allDexsDict = executeReadQuery(
        query=query
    )

    return [dexName['name'] for dexName in allDexsDict]

@lru_cache()
def getDexByDbId(dexDbId):

    query = f"SELECT dexs.* " \
            f"FROM dexs " \
            f"WHERE dexs.dex_id = '{dexDbId}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        logger.error("More Than One Dex Matches!")

