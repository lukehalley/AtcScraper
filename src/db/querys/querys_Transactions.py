from functools import lru_cache

from src.db.actions.actions_General import executeReadQuery

@lru_cache()
def getTransactionsFromDB():

    query = "" \
            f"SELECT transactions.* " \
            f"FROM transactions"

    transactions = executeReadQuery(
        query=query
    )

    return transactions

