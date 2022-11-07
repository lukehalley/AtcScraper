# Replace a value in all values in a dict
def replaceAllValuesInDict(text, dictionary):
    for key in dictionary.keys():
        text = text.replace(key, f"{dictionary[key]}")
    return text
