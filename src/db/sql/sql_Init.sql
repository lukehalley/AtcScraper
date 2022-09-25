DROP DATABASE IF EXISTS atc;
CREATE DATABASE IF NOT EXISTS atc;
USE atc;

# Networks Table
CREATE TABLE IF NOT EXISTS networks (
  # Keys
  network_id int NOT NULL AUTO_INCREMENT,
  # Fields
  name VARCHAR(64) NOT NULL UNIQUE,
#   explorer_url TEXT,
  # Key Assignments
  PRIMARY KEY (network_id),
  UNIQUE (name)
);

# Dexs Table
CREATE TABLE IF NOT EXISTS dexs (
  # Keys
  dex_id int NOT NULL AUTO_INCREMENT,
  network_id int NOT NULL,
  # Fields
  name VARCHAR(64) NOT NULL,
  # Key Assignments
  PRIMARY KEY (dex_id),
  FOREIGN KEY (network_id)
      REFERENCES networks(network_id)
      ON DELETE CASCADE,
  UNIQUE KEY unique_network_dex (network_id, name)
);

# Tokens Table
CREATE TABLE IF NOT EXISTS tokens (
  # Keys
  token_id int NOT NULL AUTO_INCREMENT,
  network_id int NOT NULL,
  # Fields
  name TEXT,
  symbol VARCHAR(64),
  address VARCHAR(64),
  # Key Assignments
  PRIMARY KEY (token_id),
  FOREIGN KEY (network_id)
      REFERENCES networks(network_id)
      ON DELETE CASCADE,
  UNIQUE KEY unique_network_token (network_id, symbol)
);

# Pairs Table
CREATE TABLE IF NOT EXISTS pairs (
  # Keys
  pair_id int NOT NULL AUTO_INCREMENT,
  primary_token_id int NOT NULL,
  secondary_token_id int NOT NULL,
  network_id int NOT NULL,
  dex_id int NOT NULL,
  # Fields
  name VARCHAR(64) NOT NULL,
  address VARCHAR(640) NOT NULL,
  ranking int NOT NULL,
  liquidity BIGINT NOT NULL,
  volume BIGINT NOT NULL,
  fdv BIGINT NOT NULL,
  # Key Assignments
  PRIMARY KEY (pair_id),
  FOREIGN KEY (network_id)
      REFERENCES networks(network_id)
      ON DELETE CASCADE,
  FOREIGN KEY (dex_id)
      REFERENCES dexs(dex_id)
      ON DELETE CASCADE,
  FOREIGN KEY (primary_token_id)
      REFERENCES tokens(token_id)
      ON DELETE CASCADE,
  FOREIGN KEY (secondary_token_id)
      REFERENCES tokens(token_id)
      ON DELETE CASCADE,
  # UNIQUE KEY unique_dex_pair (dex_id, name),
  UNIQUE KEY unique_network_pair (network_id, address)
);