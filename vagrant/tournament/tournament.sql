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
  id SERIAL PRIMARY KEY,
  winner integer NOT NULL REFERENCES players (id),
  loser integer NULL REFERENCES players (id),
  UNIQUE (winner, loser)
);
\echo 'Created "matches" table'

-- Create the player byes view
CREATE VIEW player_byes
AS
SELECT
  winner AS id,
  COUNT(CASE
    WHEN loser IS NULL THEN 1
  END) AS byes
FROM matches
GROUP BY winner;
\echo 'Created "player_byes" view'

-- Create the player standings view
CREATE VIEW player_standings
AS
SELECT
  players.id,
  name,
  COALESCE((SELECT
    COUNT(*)
  FROM matches
  WHERE players.id = matches.winner), 0) AS wins,
  (SELECT
    COUNT(*)
  FROM matches
  WHERE players.id = matches.winner
  OR players.id = matches.loser)
  AS matches,
  (CASE
    WHEN byes IS NULL THEN 0
    ELSE byes
  END)
FROM players
LEFT JOIN player_byes
  ON players.id = player_byes.id
ORDER BY wins DESC;
\echo 'Created "player_standings" view'
