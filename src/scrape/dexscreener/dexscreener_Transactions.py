import json
from pathlib import Path

from faker import Faker
from playwright.sync_api import sync_playwright, BrowserContext

from src.db.querys.querys_Networks import getNetworkRPCByDbId
from src.playwright.playwright_Hacks import safePageLoad
from src.playwright.playwright_Utils import newPage
from src.utils.data.data_ABI import loadLocalABI
from src.utils.env.env_Environment import checkHeadless
from src.utils.logging.logging_Setup import getProjectLogger, printLog

logger = getProjectLogger()

def gatherTransactionsForPair(pair):

    transactionUrl = pair["pair"]["transactions_url"]

    try:

        # Create fake user agent
        fakerInstance = Faker()
        fakeUserAgent = fakerInstance.user_agent()

        # Check if we want to start our browser in headless
        runHeadless = checkHeadless()

        # Create async instance of playwright
        with sync_playwright() as playwright:

            # Setup browser
            browser: BrowserContext = playwright.chromium.launch_persistent_context(
                headless=runHeadless,
                user_data_dir=f"{Path.home()}/.config/chromium",
                viewport={
                    "width": 1920,
                    "height": 1080
                },
                user_agent=fakeUserAgent
            )

            try:

                # Open a new tab
                page = newPage(browser=browser)

                # Navigate to the dexs url
                safePageLoad(
                    page=page,
                    url=transactionUrl
                )

                # Get JSON On Page
                innerText = page.inner_text("*")

                # Close Browser
                page.close()
                browser.close()

                # Try And Load It
                try:
                    resultJson = json.loads(innerText)
                    if resultJson['tradingHistory']:
                        transactions = resultJson['tradingHistory']
                        printLog(
                            msg=f"Got {len(resultJson['tradingHistory'])} Transactions For {resultJson['baseTokenSymbol']}/{resultJson['quoteTokenSymbol']} ✅"
                        )
                    else:
                        printLog(
                            msg=f"No Transactions For {resultJson['baseTokenSymbol']}/{resultJson['quoteTokenSymbol']} 😶"
                        )
                        transactions = None
                except:
                    printLog(
                        msg=f"Couldn't Load Any Transactions From {transactionUrl} ⛔️"
                    )
                    transactions = None

                pair["network"]["rpcUrl"] = getNetworkRPCByDbId(
                    networkDbId=pair["network"]["db"]["dbId"]
                )

                pair["dex"]["dex"]["abi"]["router_abi"] = loadLocalABI(
                    path=pair["dex"]["dex"]["abi"]["router_s3_path"]
                )

                if transactions:
                    transactionsWithPairs = [dict(transaction, **{'pairDetails': pair}) for transaction in transactions if transaction]
                    return transactionsWithPairs
                else:
                    return None

            except:

                try:
                    page.close()
                    browser.close()
                except:
                    pass

                return None

    except:

        printLog(
            msg=f"Couldn't Load Any Transactions From {transactionUrl} ⛔️"
        )
        return None

