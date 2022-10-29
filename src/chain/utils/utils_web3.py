from web3 import Web3
from web3.middleware import geth_poa_middleware

def getWeb3Instance(chainRpcURL):
    web3 = Web3(Web3.HTTPProvider(chainRpcURL))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3