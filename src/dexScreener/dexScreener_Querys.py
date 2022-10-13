import os
from decimal import Decimal

from ratelimiter import RateLimiter

from src.dexScreener.dexScreener_Utils import buildDexscreenerAPIBaseURL
from src.utils.data.data_Dictionary import replaceAllValuesInDict
from src.utils.web.web_Requests import safeRequest
from src.utils.web.web_URLs import buildApiURL

dexscreenerAPIBaseURL = buildDexscreenerAPIBaseURL()

# Get tokens pairs from Dexscreener
@RateLimiter(max_calls=300, period=60)
def getPairs(chain: int, pairAddress: str):
    initEndpoint = buildApiURL(baseUrl=dexscreenerAPIBaseURL, endpoint=os.getenv("DEXSCREENER_GET_PAIRS"))
    params = {":chainId": chain, ":pairAddress": pairAddress}
    endpoint = replaceAllValuesInDict(initEndpoint, params)
    return safeRequest(endpoint, params)


# Get tokens(s) from Dexscreener
@RateLimiter(max_calls=300, period=60)
def getTokens(tokenAddress: str):
    initEndpoint = buildApiURL(baseUrl=dexscreenerAPIBaseURL, endpoint=os.getenv("DEXSCREENER_GET_TOKENS"))
    params = {":tokenAddress": tokenAddress}
    endpoint = replaceAllValuesInDict(initEndpoint, params)
    return safeRequest(endpoint, params)

@RateLimiter(max_calls=300, period=60)
# Do a query against the Dexscreener API
def getTokensByQuery(query: str):
    initEndpoint = buildApiURL(baseUrl=dexscreenerAPIBaseURL, endpoint=os.getenv("DEXSCREENER_SEARCH_TOKENS"))
    params = {":query": query}
    endpoint = replaceAllValuesInDict(initEndpoint, params)
    return safeRequest(endpoint, params)["pairs"]


# Get the tokens price by Dex id
@RateLimiter(max_calls=300, period=60)
def getTokenPriceByDexId(chainName: str, tokenAddress: str, dexId: str):
    tokens = getTokens(tokenAddress)["pairs"]

    for token in tokens:
        if token["chainId"] == chainName and token["dexId"] == dexId:
            return Decimal(token["priceUsd"])


# Get the price of one tokens by its address
@RateLimiter(max_calls=300, period=60)
def getTokenPrice(chainName: str, tokenAddress: str):
    tokens = getTokens(tokenAddress)["pairs"]

    for token in tokens:
        if token["chainId"] == chainName:
            return Decimal(token["priceUsd"])


# Get tokens address by tokens symbol and dex name
@RateLimiter(max_calls=300, period=60)
def getTokenAddressByDexId(query: str, dexId: str):
    tokens = getTokensByQuery(query)

    for token in tokens:
        if token["dexId"] == dexId and token["baseToken"]["symbol"] == query:
            return token["baseToken"]["address"]
