from functools import lru_cache

from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

@lru_cache()
def getAllNetworks():

    query = "" \
            f"SELECT name " \
            f"FROM networks"

    allNetworksDict = executeReadQuery(
        query=query
    )

    return [networkName['name'] for networkName in allNetworksDict]

@lru_cache()
def getNetworkByDbId(networkDbId):
    query = "" \
            f"SELECT networks.* " \
            f"FROM networks " \
            f"WHERE networks.network_id='{networkDbId}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        logger.error("More Than One Network Matches!")

@lru_cache()
def getNetworkByName(networkName):
    query = "" \
            f"SELECT networks.* " \
            f"FROM networks " \
            f"WHERE name='{networkName}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]
    else:
        logger.error("More Than One Network Matches!")

@lru_cache()
def getNetworkRPCByDbId(networkDbId):

    query = f"SELECT networks.chain_rpc " \
            f"FROM networks " \
            f"WHERE networks.network_id = '{networkDbId}'"

    result = executeReadQuery(
        query=query
    )

    if len(result) < 1:
        return None
    if len(result) == 1:
        return result[0]["chain_rpc"]
    else:
        logger.error("More Than One Network Matches!")


