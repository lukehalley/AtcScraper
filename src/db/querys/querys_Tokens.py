"""Database query functions for token-related operations.

This module provides functions to query token data from the database,
including finding tokens that need address resolution.
"""
from typing import Any, List

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeReadQuery

# Placeholder value used when token address is not yet resolved
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
    """
    query = (
        f"SELECT symbol "
        f"FROM tokens "
        f"WHERE address='{ADDRESS_PLACEHOLDER}' AND network_id={networkDbId}"
    )

    cursor = getCursor(dbConnection=dbConnection)

    queryResults = executeReadQuery(
        cursor=cursor,
        query=query
    )

    return [token['symbol'] for token in queryResults]

