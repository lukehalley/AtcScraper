"""Database actions for managing trading pair records.

This module provides functions for creating and managing token pair entries
in the database, including pair creation, market data recording, and
table maintenance operations for the scraping application.

Trading pairs represent the relationship between two tokens on a DEX:
    - Primary token: The token being traded (e.g., PEPE)
    - Secondary token: The quote token (e.g., WETH, USDC)

Market data tracked for each pair includes:
    - Ranking: Position in DexScreener's top pairs list
    - Liquidity: Total liquidity locked in the pair contract
    - Volume: 24-hour trading volume
    - FDV: Fully diluted valuation

Typical usage:
    from src.db.actions.actions_Pairs import addTokenPairToDB

    await addTokenPairToDB(
        dbConnection=conn,
        networkDbId=1,
        dexDbId=1,
        primaryTokenDbId=100,
        secondaryTokenDbId=200,
        pairName="PEPE/WETH",
        pairAddress="0x...",
        pairRanking=5,
        pairLiquidity=1000000,
        pairVolume=500000,
        pairFdv=10000000
    )
"""
from typing import Any, Optional, Union

from src.db.actions.actions_Setup import getCursor
from src.db.actions.actions_General import executeWriteQuery
from src.db.querys.querys_Pairs import getPairForAddressAndNetworkId
from src.utils.logging.logging_Setup import getProjectLogger

logger = getProjectLogger()

# Table names
PAIRS_TABLE = "pairs"
MARKET_DATA_TABLE = "pair_market_data"

# Default value for numeric fields when conversion fails
DEFAULT_NUMERIC_VALUE = 0

# Log message templates for pair operations
CONVERSION_FAILED_MESSAGE = "Failed to convert '{}' to int, using default: {}"
CLEARING_TABLE_MESSAGE = "Clearing all records from {} table"
TABLE_CLEARED_MESSAGE = "Successfully cleared {} table"


def _safe_int_conversion(
    value: Union[int, str, None],
    default: int = DEFAULT_NUMERIC_VALUE
) -> int:
    """
    Safely convert a value to integer with a default fallback.

    This utility function handles the various formats that numeric data
    may arrive in from the DexScreener API, including strings, integers,
    floats, and None values.

    Args:
        value: The value to convert (can be int, str, float, or None)
        default: Default value to return if conversion fails.
            Defaults to DEFAULT_NUMERIC_VALUE (0).

    Returns:
        int: Integer value if conversion succeeds, default otherwise.

    Example:
        >>> _safe_int_conversion("1000000")
        1000000
        >>> _safe_int_conversion(None)
        0
        >>> _safe_int_conversion("invalid", default=-1)
        -1
    """
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.debug(CONVERSION_FAILED_MESSAGE.format(value, default))
        return default


async def addTokenPairToDB(
    dbConnection: Any,
    networkDbId: int,
    dexDbId: int,
    primaryTokenDbId: int,
    secondaryTokenDbId: int,
    pairName: str,
    pairAddress: str,
    pairRanking: int,
    pairLiquidity: Optional[int],
    pairVolume: Optional[int],
    pairFdv: Optional[int]
) -> None:
    """
    Add a token pair to the database or retrieve existing pair ID.
    
    This function handles the insertion of a new token pair into the database,
    including validation and type conversion of input parameters. If the pair
    already exists, it retrieves the existing pair ID instead of creating a duplicate.
    
    Args:
        dbConnection: Active database connection object
        networkDbId: Database ID of the network
        dexDbId: Database ID of the decentralized exchange
        primaryTokenDbId: Database ID of the primary token in the pair
        secondaryTokenDbId: Database ID of the secondary token in the pair
        pairName: Human-readable name of the trading pair
        pairAddress: Blockchain address of the pair contract
        pairRanking: Ranking position from DexScreener
        pairLiquidity: Liquidity value in USD
        pairVolume: Trading volume in USD
        pairFdv: Fully diluted valuation
    
    Returns:
        None (implicitly calls addPairRankToDB to store market data)
    """

    # DB Ids - use safe conversion
    primaryTokenDbId = _safe_int_conversion(primaryTokenDbId)
    secondaryTokenDbId = _safe_int_conversion(secondaryTokenDbId)
    networkDbId = _safe_int_conversion(networkDbId)
    dexDbId = _safe_int_conversion(dexDbId)

    # Strings
    pairName = str(pairName)
    pairAddress = str(pairAddress)

    # DexScreener Metadata - use safe conversion with defaults
    pairRanking = _safe_int_conversion(pairRanking)
    pairLiquidity = _safe_int_conversion(pairLiquidity)
    pairVolume = _safe_int_conversion(pairVolume)
    pairFdv = _safe_int_conversion(pairFdv)

    cursor = getCursor(dbConnection=dbConnection)

    keys = "primary_token_id, secondary_token_id, network_id, dex_id, name, address"

    selectStatement = (
        f"SELECT {primaryTokenDbId} AS primary_token_id, "
        f"{secondaryTokenDbId} AS secondary_token_id, "
        f"{networkDbId} AS network_id, "
        f"{dexDbId} AS dex_id, "
        f"'{pairName}' AS name, "
        f"'{pairAddress}' AS address"
    )

    compareStatement = f"pairs.address = '{pairAddress}' AND pairs.network_id = {networkDbId}"

    existingPairDetails = getPairForAddressAndNetworkId(
        dbConnection=dbConnection,
        pairAddress=pairAddress,
        networkDbId=networkDbId
    )

    if not existingPairDetails:

        query = (
            f"INSERT INTO pairs({keys}) "
            f"SELECT * FROM ({selectStatement}) AS tmp "
            f"WHERE NOT EXISTS "
            f"(SELECT * FROM pairs WHERE {compareStatement}) "
            f"LIMIT 1"
        )

        executeWriteQuery(
            dbConnection=dbConnection,
            cursor=cursor,
            query=query
        )

        pairDbId = cursor.lastrowid

    else:

        pairDbId = existingPairDetails["pair_id"]

    await addPairRankToDB(
        dbConnection=dbConnection,
        cursor=cursor,
        pairDbId=pairDbId,
        networkDbId=networkDbId,
        dexDbId=dexDbId,
        pairRanking=pairRanking,
        pairLiquidity=pairLiquidity,
        pairVolume=pairVolume,
        pairFdv=pairFdv,
    )


async def addPairRankToDB(
    dbConnection: Any,
    cursor: Any,
    pairDbId: int,
    networkDbId: int,
    dexDbId: int,
    pairRanking: int,
    pairLiquidity: int,
    pairVolume: int,
    pairFdv: int
) -> None:
    """
    Insert market data for a trading pair into the pair_market_data table.
    
    Records ranking, liquidity, volume, and FDV metrics for a specific pair
    on a given network and DEX. Uses INSERT with NOT EXISTS to avoid duplicates.
    
    Args:
        dbConnection: Active database connection object
        cursor: Database cursor for executing queries
        pairDbId: Database ID of the trading pair
        networkDbId: Database ID of the network
        dexDbId: Database ID of the decentralized exchange
        pairRanking: Current ranking position
        pairLiquidity: Liquidity value in USD
        pairVolume: 24h trading volume in USD
        pairFdv: Fully diluted valuation in USD
    
    Returns:
        None
    """

    keys = "pair_id, network_id, dex_id, ranking, liquidity, volume, fdv"

    selectStatement = (
        f"SELECT {pairDbId} AS pair_id, "
        f"{networkDbId} AS network_id, "
        f"{dexDbId} AS dex_id, "
        f"{pairRanking} AS ranking, "
        f"{pairLiquidity} AS liquidity, "
        f"{pairVolume} AS volume, "
        f"{pairFdv} AS fdv"
    )

    compareStatement = (
        f"pair_market_data.pair_id = '{pairDbId}' AND "
        f"pair_market_data.network_id = '{networkDbId}' AND "
        f"pair_market_data.dex_id = '{dexDbId}'"
    )

    query = (
        f"INSERT INTO pair_market_data({keys}) "
        f"SELECT * FROM ({selectStatement}) AS tmp "
        f"WHERE NOT EXISTS "
        f"(SELECT * FROM pair_market_data WHERE {compareStatement}) "
        f"LIMIT 1"
    )

    executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )


def clearPairsRankingTable(dbConnection: Any) -> Any:
    """
    Clear all records from the pair_market_data table.

    This function removes all market data entries, typically used before
    refreshing the data with updated rankings and metrics from DexScreener.

    Args:
        dbConnection: Active database connection object

    Returns:
        Result of the DELETE query execution
    """
    logger.info(CLEARING_TABLE_MESSAGE.format(MARKET_DATA_TABLE))

    query = f"DELETE FROM {MARKET_DATA_TABLE}"

    cursor = getCursor(dbConnection=dbConnection)

    result = executeWriteQuery(
        dbConnection=dbConnection,
        cursor=cursor,
        query=query
    )

    logger.debug(TABLE_CLEARED_MESSAGE.format(MARKET_DATA_TABLE))
    return result
