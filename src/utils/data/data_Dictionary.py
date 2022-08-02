import functools
from collections import OrderedDict


# Append an element to an ordered dict
def prependToOrderedDict(dictOriginal, dictAdd):
    arr = dictOriginal
    arr = OrderedDict(arr)
    new = dictAdd
    items = list(arr.items())
    items.append(new)
    arr = OrderedDict(items)
    arr.move_to_end(dictAdd[0], last=False)
    return arr


# Get the length of a dictionary
def getDictLength(sub):
    return len(sub)


# Replace a value in all values in a dict
def replaceAllValuesInDict(text, dictionary):
    return functools.reduce(lambda a, kv: a.replace(*kv), dictionary.items(), text)
