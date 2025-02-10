from distutils.util import strtobool
from typing import Union


def strToBool(x: Union[str, bool]) -> bool:
    """Convert a string to a boolean value."""
    if isinstance(x, bool):
        return x
    else:
        return bool(strtobool(x))
