from eth_utils import to_hex

def decodeList(l):
    decodeLst = l
    for i in range(len(l)):
        if isinstance(l[i], (bytes, bytearray)):
            decodeLst[i] = to_hex(l[i])
        else:
            decodeLst[i] = l[i]
    return decodeLst