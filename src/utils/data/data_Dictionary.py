"""
Dictionary manipulation utilities for common operations.

Provides helper functions for working with dictionaries including
prepending to ordered dicts and string replacement operations.
"""
import functools
from collections import OrderedDict
from typing import Any, Dict, Tuple

# Type aliases for clarity
KeyValuePair = Tuple[Any, Any]
ReplacementMap = Dict[str, str]


def prependToOrderedDict(
    dictOriginal: Dict[Any, Any],
    dictAdd: KeyValuePair
) -> OrderedDict:
    """
    Add an element to an ordered dict and move it to the front.

    Creates a new OrderedDict with the added element at the beginning
    while preserving the order of existing elements.

    Args:
        dictOriginal: The original dictionary to modify
        dictAdd: A tuple of (key, value) to add at the front

    Returns:
        New OrderedDict with the element prepended
    """
    arr = OrderedDict(dictOriginal)
    items = list(arr.items())
    items.append(dictAdd)
    arr = OrderedDict(items)
    arr.move_to_end(dictAdd[0], last=False)
    return arr


def getDictLength(dictionary: Dict[Any, Any]) -> int:
    """
    Get the number of key-value pairs in a dictionary.

    Args:
        dictionary: The dictionary to measure

    Returns:
        Number of items in the dictionary, or 0 if None is passed

    Examples:
        >>> getDictLength({'a': 1, 'b': 2})
        2
        >>> getDictLength({})
        0
        >>> getDictLength(None)
        0
    """
    if dictionary is None:
        return 0
    return len(dictionary)


def replaceAllValuesInDict(text: str, replacements: ReplacementMap) -> str:
    """
    Replace all occurrences of dictionary keys with their values in text.

    Iteratively applies string replacements using the dictionary's
    key-value pairs. Each key found in the text is replaced with
    its corresponding value.

    Args:
        text: The original string to modify
        replacements: Dictionary mapping strings to find to replacement values

    Returns:
        Modified string with all replacements applied
    """
    return functools.reduce(
        lambda a, kv: a.replace(*kv),
        replacements.items(),
        text
    )
