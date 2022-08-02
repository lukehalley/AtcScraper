import time

from src.utils.logging.logging_Setup import getProjectLogger
from src.utils.time.time_Calculations import getMinSecString

logger = getProjectLogger()

telegramSeperator = "-------------------------------"

# # Print the current round trip count
# def printRoundtrip(roundtrip):
#
#     logger.info("################################")
#     logger.info(f"STARTING ARBITRAGE #{roundtrip}")
#     logger.info("################################\n")
#
#
# # Print the Arbitrage is profitable alert
# def printSettingUpWallet(count):
#     from src.apis.telegramBot.telegramBot_Action import sendMessage
#
#     logger.info("--------------------------------")
#     logger.info(f" Correcting Wallet Setup State ")
#
#     sentMessage = sendMessage(
#         msg=
#         f"Arbitrage #{count} Setup ⚙️\n"
#         f"Tokens -> Stables"
#     )
#
#     return sentMessage
#
#
# # Print the Arbitrage is profitable alert
# def printArbitrageProfitable(recipe):
#     from src.apis.telegramBot.telegramBot_Action import sendMessage
#
#     count = recipe['status']['currentRoundTrip']
#     networkPath = f'{recipe["origin"]["chain"]["name"]} -> {recipe["destination"]["chain"]["name"]}'
#     tokenPath = f'{recipe["origin"]["token"]["symbol"]} -> {recipe["destination"]["token"]["symbol"]}'
#
#     logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#     logger.info(f"ARBITRAGE #{count} PROFITABLE")
#     logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
#
#     sentMessage = sendMessage(
#         msg=
#         f"{telegramSeperator}\n"
#         f"| Arbitrage #{count} Profitable 🤑 |\n"
#         f"{telegramSeperator}\n"
#         f"[ Network Path ]\n"
#         f"- {networkPath}\n"
#         f"[ Token Path ]\n"
#         f"- {tokenPath}\n"
#         f"[ Return ]\n"
#         f"- ${recipe['arbitrage']['predictions']['startingStables']} -> ${recipe['arbitrage']['predictions']['outStables']}\n"
#         f"[ Profit ]\n"
#         f"- ${recipe['arbitrage']['predictions']['profitLoss']} ({recipe['arbitrage']['predictions']['arbitragePercentage']}%)\n"
#         f"{telegramSeperator}\n"
#         f"[ Execution ⏭ ] \n"
#     )
#
#     recipe["status"]["telegramStatusMessage"] = sentMessage
#
#     return recipe
#
#
# # Print the Arbitrage is profitable alert
# def printArbitrageComplete(recipe, wasRollback, wasProfitable, profitLoss, profitPercentage):
#     from src.apis.telegramBot.telegramBot_Action import appendToMessage, sendMessage
#     from src.apis.firebaseDB.firebaseDB_Actions import writeResultToDB
#
#     profitLoss = round(profitLoss, 2)
#
#     originStables = round(recipe["origin"]["wallet"]["balances"]["stablecoin"], 2)
#
#     originGasBalance = round(recipe["origin"]["wallet"]["balances"]["gas"], 2)
#     originGasSymbol = recipe["origin"]["gas"]["symbol"]
#     originGasStr = f"{originGasBalance} {originGasSymbol}"
#
#     destinationGasBalance = round(recipe["destination"]["wallet"]["balances"]["gas"], 2)
#     destinationGasSymbol = recipe["destination"]["gas"]["symbol"]
#     destinationGasStr = f"{destinationGasBalance} {destinationGasSymbol}"
#
#     finishingTime = time.perf_counter()
#     timeTook = finishingTime - recipe["status"]["startingTime"]
#
#     if wasRollback:
#         typeString = f"Rollback"
#         separatorString = "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
#     else:
#         separatorString = "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
#         typeString = f"Arbitrage"
#
#     timeString = f"Completed {typeString} In {getMinSecString(timeTook)}"
#
#     printSeparator()
#     logger.info(separatorString)
#     logger.info(f"{typeString} #{recipe['status']['currentRoundTrip']} Done")
#
#     if wasProfitable:
#         logger.info(f"Made A Profit Of ${profitLoss} ({profitPercentage}%)")
#         appendToMessage(messageToAppendTo=recipe["status"]["telegramStatusMessage"],
#                         messageToAppend=
#                         f"{telegramSeperator}\n"
#                         f"[ Results ]\n"
#                         f"- Profit Of ${round(profitLoss, 2)} ({profitPercentage}%) 👍\n"
#                         f"[ Stable Balance ] \n"
#                         f"- ${originStables}\n"
#                         f"[ Gas Balances ] \n"
#                         f"- Origin: {originGasStr}\n"
#                         f"- Destination: {destinationGasStr}\n"
#                         f"{telegramSeperator}\n"
#                         )
#     else:
#         logger.info(f"Made A Loss Of ${profitLoss} ({profitPercentage}%)")
#         appendToMessage(messageToAppendTo=recipe["status"]["telegramStatusMessage"],
#                         messageToAppend=
#                         f"{telegramSeperator}\n"
#                         f"[ Results ]\n"
#                         f"- Loss Of ${round(profitLoss, 2)} ({profitPercentage}%) 👎\n"
#                         f"[ Stable Balance ] \n"
#                         f"- ${originStables}\n"
#                         f"[ Gas Balances ] \n"
#                         f"- Origin: {originGasStr}\n"
#                         f"- Destination: {destinationGasStr}\n"
#                         f"{telegramSeperator}\n"
#                         )
#
#     logger.info(f"New Stable Balance: ${originStables}")
#     logger.info(f"New Origin Gas Balance: {originGasStr}")
#     logger.info(f"New Destination Gas Balance: {destinationGasStr}")
#
#     logger.info(timeString)
#     logger.info(separatorString)
#
#     sendMessage(msg="@lukehalley done")
#
#     logger.info("Writing result to Firebase...")
#     result = {
#         "wasProfitable": wasProfitable,
#         "arbitrageStrategy": recipe["arbitrage"]["strategies"]["arbitrage"],
#         "profitLoss": profitLoss,
#         "percentageDifference": profitPercentage,
#         "timeTookSeconds": timeTook,
#         "wasRollback": wasRollback,
#
#     }
#     writeResultToDB(result=result, currentRoundTrip=recipe['status']['currentRoundTrip'])
#     logger.info("Result written to Firebase ✅")
#     printSeparator(newLine=True)
#
#     return


# Print a separator line
def printSeparator(newLine=False):
    if newLine:
        line = ("--------------------------------\n")
    else:
        line = ("--------------------------------")

    logger.info(line)
