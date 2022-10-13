import os


# Build the base of our API endpoint url
def buildDexscreenerAPIBaseURL():
    dexscreenerAPIEndpoint = os.getenv("DEXSCREENER_API_ENDPOINT")
    dexscreenerAPIVersion = os.getenv("DEXSCREENER_API_VERSION")
    dexscreenerAPISection = os.getenv("DEXSCREENER_API_SECTION")
    return dexscreenerAPIEndpoint + "/" + dexscreenerAPIVersion + "/" + dexscreenerAPISection
