from distutils.util import strtobool


# Convert a str to a bool
def strToBool(x):
    if type(x) == bool:
        return x
    else:
        return bool(strtobool(x))
