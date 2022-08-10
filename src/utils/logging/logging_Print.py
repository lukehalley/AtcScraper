from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Print a separator line
def printSeparator(newLine=False):
    if newLine:
        line = "--------------------------------\n"
    else:
        line = "--------------------------------"

    logger.info(line)
