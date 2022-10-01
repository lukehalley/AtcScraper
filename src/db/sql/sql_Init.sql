DROP DATABASE IF EXISTS atc;
CREATE DATABASE IF NOT EXISTS atc;
USE atc;

# Networks Table
CREATE TABLE IF NOT EXISTS networks (
  # Keys
  network_id int NOT NULL AUTO_INCREMENT,
  # Fields
  name VARCHAR(64) NOT NULL UNIQUE,
  # Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
  # Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
  # Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
  # Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
  UNIQUE KEY unique_network_pair (network_id, address)
);

# Pair Ranks Table
CREATE TABLE IF NOT EXISTS pair_market_data (
  # Keys
  pair_marketdata_id int NOT NULL AUTO_INCREMENT,
  pair_id int NOT NULL,
  network_id int NOT NULL,
  dex_id int NOT NULL,
  # Fields
  ranking int NOT NULL,
  liquidity BIGINT NOT NULL,
  volume BIGINT NOT NULL,
  fdv BIGINT NOT NULL,
  # Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  # Key Assignments
  PRIMARY KEY (pair_marketdata_id),
  FOREIGN KEY (pair_id)
      REFERENCES pairs(pair_id)
      ON DELETE CASCADE,
  FOREIGN KEY (network_id)
      REFERENCES networks(network_id)
      ON DELETE CASCADE,
  FOREIGN KEY (dex_id)
      REFERENCES dexs(dex_id)
      ON DELETE CASCADE
);