import json


def loadLocalABI(path):

    abi = json.load(open(f'data/mapped-abis/{path}'))["abi"]

    return abi