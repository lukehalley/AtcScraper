import json
from functools import lru_cache

from web3 import Web3
from web3.auto import w3

@lru_cache(maxsize=None)
def getContract(address, abi):
    if isinstance(abi, str):
        abi = json.loads(abi)
    contract = w3.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)
    return contract, abi