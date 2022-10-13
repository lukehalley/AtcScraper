def cleanString(string):
    if string:
        return string.replace(r"'", "").replace(r'"', '')
    else:
        return None