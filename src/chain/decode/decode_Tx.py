import sys

from eth_utils import to_int

from src.chain.abi.abi_Contract import getContract
from src.chain.convert.convert_Hex import convertToHex

def decodeTx(address, transaction, abi):

    inputData = transaction["input"]
    blockNumber = int(transaction["blockNumber"])

    if abi is not None:
        try:
            (contract, abi) = getContract(address, abi)
            func_obj, func_params = contract.decode_function_input(inputData)
            target_schema = [a['inputs'] for a in abi if 'name' in a and a['name'] == func_obj.fn_name][0]
            decoded_func_params = convertToHex(func_params, target_schema)

            result = {
                "name": func_obj.fn_name,
                "params": decoded_func_params,
                "schema": target_schema,
                "blockNumber": blockNumber,
                "txHash":transaction["hash"],
                "timestamp": transaction["timeStamp"]
            }

            return result
        except:
            e = sys.exc_info()[0]
            return 'decode error', repr(e), None
    else:
        return 'no matching abi', None, None