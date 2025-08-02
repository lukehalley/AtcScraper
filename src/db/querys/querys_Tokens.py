"""Database query functions for token-related operations.

This module provides functions to query token data from the database,
including finding tokens that need address resolution. Token queries
are essential for tracking which tokens have complete metadata and
which still require contract address discovery from DexScreener.

Typical usage:
    from src.db.querys.querys_Tokens import getTokensForChainWithNoAddress

    # Get tokens needing address resolution for Ethereum (network_id=1)
    missing_address_tokens = getTokensForChainWithNoAddress(db_conn, 1)
    for token_symbol in missing_address_tokens:
        # Process each token...
"""
from typing import Any, List

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Table and column names
TOKENS_TABLE = "tokens"
SYMBOL_COLUMN = "symbol"
ADDRESS_COLUMN = "address"
NETWORK_ID_COLUMN = "network_id"

# Placeholder value used when token address is not yet resolved
# This value is inserted during initial token creation and updated
# when the contract address is scraped from the token detail page
ADDRESS_PLACEHOLDER = "None"


def getTokensForChainWithNoAddress(
    dbConnection: Any,
    networkDbId: int
) -> List[str]:
    """
    Retrieve all token symbols that don't have a contract address.

    Finds tokens on a specific network where the address field contains
    the placeholder value, indicating the address has not yet been
    scraped from the token's detail page.

    Args:
        dbConnection: Active database connection object
        networkDbId: Database ID of the network to query tokens for

    Returns:
        List[str]: List of token symbols without addresses

    Example:
        >>> tokens = getTokensForChainWithNoAddress(conn, network_id=1)
        >>> print(tokens)
        ['PEPE', 'SHIB', 'DOGE']
    """
    # Build query using table/column constants for maintainability
    query = (
        f"SELECT {SYMBOL_COLUMN} "
        f"FROM {TOKENS_TABLE} "
        f"WHERE {ADDRESS_COLUMN}='{ADDRESS_PLACEHOLDER}' "
        f"AND {NETWORK_ID_COLUMN}={networkDbId}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    queryResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    # Extract symbol values from query results
    token_symbols = [token[SYMBOL_COLUMN] for token in queryResults]

    logger.debug(
        f"Found {len(token_symbols)} tokens without addresses "
        f"on network ID {networkDbId}"
    )

    return token_symbols

