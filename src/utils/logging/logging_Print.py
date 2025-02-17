from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Default separator character and length
SEPARATOR_CHAR = "-"
SEPARATOR_LENGTH = 32


def printSeparator(newLine: bool = False) -> None:
    """
    Print a visual separator line to the log output.

    Args:
        newLine: If True, appends a newline character after the separator
                 for additional visual spacing in logs.

    Returns:
        None
    """
    separator = SEPARATOR_CHAR * SEPARATOR_LENGTH
    if newLine:
        separator += "\n"

    logger.info(separator)
