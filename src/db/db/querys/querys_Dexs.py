import os

from src.db.actions.actions_General import executeReadQuery
from src.db.actions.actions_Setup import getCursor
from src.sniffer.sniffer_Process import processDexInformation
from src.utils.data.data_Booleans import strToBool
from src.utils.logging.logging_Print import printSeparator
from src.utils.logging.logging_Setup import getProjectLogger

logger= getProjectLogger()

def getAllDexsWithABIs(dbConnection):

    lazyMode = strToBool(os.getenv("LAZY_MODE"))

    conditions = "(dexs.factory IS NOT NULL AND dexs.factory!='') " \
                 "AND " \
                 "(dexs.factory_s3_path IS NOT NULL AND dexs.factory_s3_path!='') " \
                 "AND " \
                 "(dexs.router IS NOT NULL AND dexs.router!='')" \
                 "AND " \
                 "(dexs.router_s3_path IS NOT NULL AND dexs.router_s3_path!='')" \
                 "AND (networks.explorer_type='scan' OR networks.explorer_type='blockscout')"

    query = "" \
            f"SELECT dexs.* " \
            f"FROM dexs " \
            f"JOIN networks ON dexs.network_id = networks.network_id " \
            f"WHERE {conditions}"

    cursor = getCursor(dbConnection=dbConnection)

    dexs = executeReadQuery(
        cursor=cursor,
        query=query
    )

    if lazyMode:
        dexs = dexs[0:9]

    dexCount = len(dexs)
    logger.info(f"Retrieved {dexCount} Dexs From DB")
    printSeparator()

    finalDexs = []
    cachedNetworkDetails = {}
    for dex in dexs:
        dexIndex = dexs.index(dex)

        try:
            processedDex, cachedNetworkDetails = processDexInformation(
                dbConnection=dbConnection,
                dex=dex,
                dexIndex=dexIndex,
                dexCount=dexCount,
                cachedNetworkDetails=cachedNetworkDetails
            )

            finalDexs.append(processedDex)

            if lazyMode:
                break
        except:
            x = 1
            continue

    printSeparator(True)

    return finalDexs
