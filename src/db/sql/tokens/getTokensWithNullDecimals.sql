SELECT
  tokens.token_id,
  tokens.network_id,
  networks.name,
  networks.chain_rpc,
  tokens.symbol,
  tokens.address
FROM
  tokens
  JOIN networks ON tokens.network_id = networks.network_id
WHERE
  tokens.decimals IS NULL