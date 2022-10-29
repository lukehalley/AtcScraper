from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Setup import getCursor
from src.utils.data.data_ABI import loadLocalABI
from src.utils.logging.logging_Setup import getProjectLogger

logger= getProjectLogger()

def getDexRouterDetailsByDbId(dbConnection, dexDbid):

    query = "" \
            f"SELECT dexs.router, dexs.router_s3_path " \
            f"FROM dexs " \
            f"WHERE dexs.dex_id = {dexDbid}"

    cursor = getCursor(dbConnection=dbConnection)

    dexInfo = executeReadQuery(
        cursor=cursor,
        query=query
    )

    router = dexInfo[0]["router"][0:42]
    routerAbi = loadLocalABI(path=dexInfo[0]["router_s3_path"])

    return router, routerAbi
