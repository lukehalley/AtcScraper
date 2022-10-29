import json
from web3.middleware import geth_poa_middleware
from web3 import Web3, HTTPProvider

from src.chain.abi.abi_Contract import getContract
from src.chain.convert.convert_Hex import convertToHex

def decodeTx(contractAddress, rpcUrl, transactionHash, abi):

    web3 = Web3(Web3.HTTPProvider(rpcUrl))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    transaction = web3.eth.get_transaction(transactionHash)

    inputData = transaction["input"]
    blockNumber = int(transaction["blockNumber"])

    if abi is not None:
        (contract, abi) = getContract(contractAddress, json.dumps(abi))
        try:
            func_obj, func_params = contract.decode_function_input(inputData)
            target_schema = [a['inputs'] for a in abi if 'name' in a and a['name'] == func_obj.fn_name][0]
            decoded_func_params = convertToHex(func_params, target_schema)

            timestamp = web3.eth.getBlock(blockNumber).timestamp

            result = {
                "name": func_obj.fn_name,
                "params": decoded_func_params,
                "schema": target_schema,
                "blockNumber": blockNumber,
                "txHash": transaction["hash"],
                "timestamp": timestamp
            }

            return result
        except:
            pass
    else:
        return 'no matching abi', None, None