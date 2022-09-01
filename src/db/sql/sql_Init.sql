DROP DATABASE IF EXISTS atc;
CREATE DATABASE IF NOT EXISTS atc;
USE atc;

# Networks Table
CREATE TABLE IF NOT EXISTS networks (
  # Keys
  network_id int NOT NULL AUTO_INCREMENT,
  # Fields
  name TEXT NOT NULL,
  # Key Assignments
  PRIMARY KEY (network_id)
);

# Dexs Table
CREATE TABLE IF NOT EXISTS dexs (
  # Keys
  dex_id int NOT NULL AUTO_INCREMENT,
  network_id int NOT NULL,
  # Fields
  name TEXT NOT NULL,
  # Key Assignments
  PRIMARY KEY (dex_id),
  FOREIGN KEY (network_id)
      REFERENCES networks(network_id)
      ON DELETE CASCADE
);

# Tokens Table
CREATE TABLE IF NOT EXISTS tokens (
  # Keys
  token_id int NOT NULL AUTO_INCREMENT,
  network_id int NOT NULL,
  # Fields
  name TEXT,
  symbol TEXT NOT NULL,
  address TEXT,
  # Key Assignments
  PRIMARY KEY (token_id),
  FOREIGN KEY (network_id)
      REFERENCES networks(network_id)
      ON DELETE CASCADE
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
  name TEXT NOT NULL,
  address TEXT NOT NULL,
  ranking int NOT NULL,
  price decimal NOT NULL,
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
      ON DELETE CASCADE
);