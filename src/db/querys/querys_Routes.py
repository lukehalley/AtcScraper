from functools import lru_cache

from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

def getPairsWithRoutes():
    query = "SELECT DISTINCT pair_id FROM routes WHERE pair_id"

    pairsWithRoutes = executeReadQuery(
        query=query
    )

    return [pairsWithRoute['pair_id'] for pairsWithRoute in pairsWithRoutes]

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

