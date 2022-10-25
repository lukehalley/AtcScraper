def replaceTrailingDigitsWithZeros(number):
    leadingNumber = str(number)[0]
    zerosToAdd = len(str(number)) - 1
    return int(f"{leadingNumber}{'0' * zerosToAdd}")