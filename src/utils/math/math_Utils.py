def replaceTrailingDigitsWithZeros(number: int) -> int:
    """Replace all trailing digits with zeros, keeping only the leading digit."""
    leadingNumber = str(number)[0]
    zerosToAdd = len(str(number)) - 1
    return int(f"{leadingNumber}{'0' * zerosToAdd}")