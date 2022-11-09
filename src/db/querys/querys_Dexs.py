from src.db.actions.actions_General import executeReadQuery
import json

from src.db.actions.actions_General import executeReadQuery
from src.utils.data.data_ABI import loadLocalABI
from src.utils.logging.logging_Setup import getProjectLogger

logger= getProjectLogger()

def getDexRouterDetailsByDbId(dexDbid):

    query = "" \
            f"SELECT dexs.router, dexs.router_s3_path " \
            f"FROM dexs " \
            f"WHERE dexs.dex_id = {dexDbid}"

    dexInfo = executeReadQuery(
        query=query
    )

    try:

        router = dexInfo[0]["router"][0:42]
        routerAbi = loadLocalABI(path=dexInfo[0]["router_s3_path"])

        finalRouterAbi = json.dumps(routerAbi)

        return router, finalRouterAbi

    except:

        return None, None

def getDexByNameAndNetworkId(dexName, networkId):

    query = "" \
            f"SELECT dexs.* " \
            f"FROM dexs " \
            f"WHERE dexs.name = '{dexName}' AND dexs.network_id = {networkId}"

    dexInfo = executeReadQuery(
        query=query
    )

    return dexInfo[0]


def getAllDexsForNetwork(networkDbId):

    query = "" \
            f"SELECT name " \
            f"FROM dexs " \
            f"WHERE network_id={networkDbId}"

    allDexsDict = executeReadQuery(
        query=query
    )

    return [dexName['name'] for dexName in allDexsDict]

