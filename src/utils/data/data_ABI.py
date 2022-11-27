import json
from functools import lru_cache

@lru_cache()
def loadLocalABI(path):

    abi = json.load(open(f'data/mapped-abis/{path}'))["abi"]

    return abi