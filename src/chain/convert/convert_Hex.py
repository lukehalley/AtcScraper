from eth_utils import to_hex

from src.chain.decode.decode_List import decodeList
from src.chain.decode.decode_Tuple import decodeTuples, decodeTuple


def convertToHex(arg, target_schema):
    hexDict = dict()
    for k in arg:
        if isinstance(arg[k], (bytes, bytearray)):
            hexDict[k] = to_hex(arg[k])
        elif isinstance(arg[k], list) and len(arg[k]) > 0:
            target = [a for a in target_schema if 'name' in a and a['name'] == k][0]
            if target['type'] == 'tuple[]':
                target_field = target['components']
                hexDict[k] = decodeTuples(arg[k], target_field)
            else:
                hexDict[k] = decodeList(arg[k])
        elif isinstance(arg[k], tuple):
            target_field = [a['components'] for a in target_schema if 'name' in a and a['name'] == k][0]
            hexDict[k] = decodeTuple(arg[k], target_field)
        else:
            hexDict[k] = arg[k]
    return hexDict