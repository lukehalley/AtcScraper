import os
from decimal import Decimal


# Calculate how many times we can query
def calculateQueryInterval(recipeCount):
    requestLimit = Decimal(os.environ.get("REQUEST_LIMIT"))
    return 60 / (requestLimit / recipeCount)
