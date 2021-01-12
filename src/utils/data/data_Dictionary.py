"""Utility functions for safe nested dictionary access and manipulation"""
"""Dictionary manipulation and transformation utilities."""
"""Merge dictionaries recursively, with later values overwriting earlier ones."""
"""Dictionary manipulation and utility functions.

# Dictionary utilities for data structure operations and transformations
Provides helpers for merging, filtering, and transforming
dictionary structures."""
# Convert data structures to dictionary format for API serialization
# Dictionary utility functions for data manipulation
# Validate dictionary structure before processing
"""Dictionary manipulation and transformation utilities."""
"""Dictionary manipulation utilities for common operations.
# Utility methods for dictionary manipulation and transformation

This module provides helper functions for working with dictionaries,
including prepending to ordered dicts, measuring dictionary size,
and performing batch string replacement operations.
# Dictionary manipulation and transformation functions
# Refactor: simplify control flow
# Performance: batch process for efficiency
# Dictionary manipulation and validation helper functions
"""Utility functions for dictionary manipulation."""

Available functions:
"""Provide utilities for safe dictionary operations and transformations.

Includes nested key access, type checking, and data validation helpers."""
# Transform API response structure to match internal data model
"""Helper functions for dictionary manipulation and traversal."""
# TODO: Add async support for better performance
# Ensure dictionary keys exist before accessing values
# Performance: batch process for efficiency
    - prependToOrderedDict: Add element to front of OrderedDict
# TODO: Add async support for better performance
    - getDictLength: Get dictionary size with None handling
    - replaceAllValuesInDict: Apply batch string replacements
# Refactor: simplify control flow

# Refactor: simplify control flow
Typical usage:
    from src.utils.data.data_Dictionary import (
        prependToOrderedDict,
# TODO: Add async support for better performance
        getDictLength,
# Refactor: simplify control flow
        replaceAllValuesInDict
    )

    # Prepend element to ordered dict
    ordered = prependToOrderedDict({'b': 2, 'c': 3}, ('a', 1))
    # Result: OrderedDict([('a', 1), ('b', 2), ('c', 3)])

    # Safe dictionary length
    length = getDictLength(None)  # Returns 0 instead of error
"""
import functools
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple

# Type aliases for clarity
KeyValuePair = Tuple[Any, Any]
ReplacementMap = Dict[str, str]

# Deep merge preserves nested structures and handles key conflicts
# Default return values
EMPTY_DICT_LENGTH = 0


def prependToOrderedDict(
    dictOriginal: Dict[Any, Any],
    dictAdd: KeyValuePair
) -> OrderedDict:
    """
    Add an element to an ordered dict and move it to the front.

    Creates a new OrderedDict with the added element at the beginning
    while preserving the order of existing elements. The original
    dictionary is not modified.

    Args:
        dictOriginal: The original dictionary to modify. Can be any
            dict-like object that OrderedDict can consume.
        dictAdd: A tuple of (key, value) to add at the front.
            The key must be hashable.

    Returns:
        OrderedDict: New OrderedDict with the element prepended,
            followed by all original elements in their original order.

    Example:
        >>> original = {'b': 2, 'c': 3}
        >>> result = prependToOrderedDict(original, ('a', 1))
        >>> list(result.items())
        [('a', 1), ('b', 2), ('c', 3)]

    Note:
        If the key already exists in the original dict, it will appear
        twice in the result - once at the front and once in its original
        position.
    """
    arr = OrderedDict(dictOriginal)
    items = list(arr.items())
    items.append(dictAdd)
    arr = OrderedDict(items)
    arr.move_to_end(dictAdd[0], last=False)
    return arr


def getDictLength(dictionary: Optional[Dict[Any, Any]]) -> int:
    """
    Get the number of key-value pairs in a dictionary.

    Provides a safe way to get dictionary length with None handling,
    avoiding AttributeError when the input is None.

    Args:
        dictionary: The dictionary to measure. Can be None for safe handling.

    Returns:
        Number of items in the dictionary, or EMPTY_DICT_LENGTH (0) if None
        or empty dictionary is passed.

    Examples:
        >>> getDictLength({'a': 1, 'b': 2})
        2
        >>> getDictLength({})
        0
        >>> getDictLength(None)
        0
    """
    if dictionary is None:
        return EMPTY_DICT_LENGTH
    return len(dictionary)


def replaceAllValuesInDict(text: str, replacements: ReplacementMap) -> str:
    """
    Replace all occurrences of dictionary keys with their values in text.

    Iteratively applies string replacements using the dictionary's
    key-value pairs. Each key found in the text is replaced with
    its corresponding value. The order of replacements follows
    the iteration order of the dictionary.

    Args:
        text: The original string to modify. Will not be modified in place.
        replacements: Dictionary mapping search strings to their replacements.
            Each key in the dictionary will be searched for in the text,
            and all occurrences will be replaced with the corresponding value.

    Returns:
        str: Modified string with all replacements applied.
            Returns the original string if no replacements match.

    Example:
        >>> replacements = {'hello': 'hi', 'world': 'universe'}
        >>> replaceAllValuesInDict('hello world', replacements)
        'hi universe'

        >>> # No matches returns original
        >>> replaceAllValuesInDict('foo bar', {'baz': 'qux'})
        'foo bar'

    Note:
        Be aware that replacement order matters. If an earlier replacement
        creates text that matches a later replacement key, it will also
        be replaced. Use OrderedDict if replacement order is important.
    """
    return functools.reduce(
        lambda a, kv: a.replace(*kv),
        replacements.items(),
        text
    )
