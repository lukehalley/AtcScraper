SELECT
  pairs.pair_id AS pair_db_id,
  pairs.analysed AS pairs_analysed,
  pairs.name AS pair_name,
  pairs.address AS pair_address,
  primary_tokens.token_id AS primary_token_db_id,
  primary_tokens.symbol AS primary_token_symbol,
  primary_tokens.address AS primary_token_address,
  secondary_tokens.token_id AS secondary_token_db_id,
  secondary_tokens.symbol AS secondary_token_symbol,
  secondary_tokens.address AS secondary_token_address,
  networks.network_id AS network_db_id,
  networks.name AS network_name,
  networks.chain_number AS network_chain_number
FROM
  (
    pairs
    JOIN tokens AS primary_tokens ON pairs.primary_token_id = primary_tokens.token_id
    JOIN tokens AS secondary_tokens ON pairs.secondary_token_id = secondary_tokens.token_id
    JOIN networks ON pairs.network_id = networks.network_id
  )
WHERE
  NOT pairs.analysed AND
  (primary_tokens.address IS NULL
  OR secondary_tokens.address IS NULL)
ORDER BY
  pairs.primary_token_id,
  pairs.secondary_token_id,
  pairs.dex_id,
  pairs.network_id;