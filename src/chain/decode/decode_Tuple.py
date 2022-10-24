from eth_utils import to_hex

def decodeTuple(t, target_field):
    decodeDict = dict()
    for i in range(len(t)):
        if isinstance(t[i], (bytes, bytearray)):
            decodeDict[target_field[i]['name']] = to_hex(t[i])
        elif isinstance(t[i], tuple):
            decodeDict[target_field[i]['name']] = decodeTuple(t[i], target_field[i]['components'])
        else:
            decodeDict[target_field[i]['name']] = t[i]
    return decodeDict


def decodeTuples(l, target_field):
    decodeLst = l
    for i in range(len(l)):
        decodeLst[i] = decodeTuple(l[i], target_field)
    return decodeLst