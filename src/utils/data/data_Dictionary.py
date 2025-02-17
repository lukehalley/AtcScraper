import functools
from collections import OrderedDict
from typing import Any, Dict, Tuple


def prependToOrderedDict(dictOriginal: Dict[Any, Any], dictAdd: Tuple[Any, Any]) -> OrderedDict:
    """Append an element to an ordered dict and move it to the front."""
    arr = OrderedDict(dictOriginal)
    items = list(arr.items())
    items.append(dictAdd)
    arr = OrderedDict(items)
    arr.move_to_end(dictAdd[0], last=False)
    return arr


def getDictLength(sub: Dict[Any, Any]) -> int:
    """Get the length of a dictionary."""
    return len(sub)


def replaceAllValuesInDict(text: str, dictionary: Dict[str, str]) -> str:
    """Replace all occurrences of keys with values from dictionary in text."""
    return functools.reduce(lambda a, kv: a.replace(*kv), dictionary.items(), text)
