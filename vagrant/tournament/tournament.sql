-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Drop the database if already exists and then create the new one
\echo 'Delete "tournament" database if already exists'
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\echo 'Created "tournament" database'

-- Connect to the database so that we can create tables in it
\echo 'Connecting to the database'
\c tournament;

-- Create the 'players' table to keep track of players information
CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  name text NOT NULL CHECK (name <> '')
);
\echo 'Created "players" table'

-- Create the 'matches' table to keep track of matches
CREATE TABLE matches (
  winner integer NOT NULL REFERENCES players (id),
  loser integer NOT NULL REFERENCES players (id),
  PRIMARY KEY (winner, loser)
);
\echo 'Created "matches" table'

-- Create the player standings view
CREATE VIEW player_standings
AS
SELECT
  id,
  name,
  COALESCE((SELECT
    COUNT(*)
  FROM matches
  WHERE id = matches.winner), 0) AS wins,
  (SELECT
    COUNT(*)
  FROM matches
  WHERE id = matches.winner
  OR id = matches.loser)
  AS matches
FROM players
ORDER BY wins DESC;
\echo 'Created "player_standings" view'
