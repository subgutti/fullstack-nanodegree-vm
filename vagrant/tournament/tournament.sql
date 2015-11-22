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

-- Create the 'tournament' table to keep track of tournaments
CREATE TABLE tournament (
  id SERIAL PRIMARY KEY,
  name text NOT NULL CHECK (name <> ''),
  created_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
\echo 'Created "tournament" table'

-- Create the 'players' table to keep track of players information
CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  name text NOT NULL CHECK (name <> ''),
  tournament_id integer REFERENCES tournament(id)
);
\echo 'Created "players" table'

-- Create the 'matches' table to keep track of matches
-- 'null' value in loser, means that match is a bye
CREATE TABLE matches (
  id SERIAL PRIMARY KEY,
  tournament_id integer REFERENCES tournament(id),
  winner integer NOT NULL REFERENCES players (id),
  loser integer NULL REFERENCES players (id),
  UNIQUE (winner, loser)
);
\echo 'Created "matches" table'

-- Create the current tournament view
CREATE VIEW current_tournament
AS
SELECT
  id
FROM tournament
ORDER BY created_time DESC
LIMIT 1;
\echo 'Created "current_tournament" view'

-- Create the current players view
CREATE VIEW current_players
AS
SELECT
  id,
  name
FROM players
WHERE tournament_id = (SELECT * FROM current_tournament);
\echo 'Created "current_players" view'

-- Create the current matches view
CREATE VIEW current_matches
AS
SELECT
  id,
  winner,
  loser
FROM matches
WHERE tournament_id = (SELECT * FROM current_tournament);
\echo 'Created "current_matches" view'

-- Create the current player byes view
CREATE VIEW current_player_byes
AS
SELECT
  winner AS id,
  COUNT(CASE
    WHEN loser IS NULL THEN 1
  END) AS byes
FROM current_matches
GROUP BY winner;
\echo 'Created "current_player_byes" view'

-- Create the current player standings view
CREATE VIEW current_player_standings
AS
SELECT
  current_players.id,
  name,
  COALESCE((SELECT
    COUNT(*)
  FROM current_matches
  WHERE current_players.id = current_matches.winner), 0) AS wins,
  (SELECT
    COUNT(*)
  FROM current_matches
  WHERE current_players.id = current_matches.winner
  OR current_players.id = current_matches.loser)
  AS matches,
  (CASE
    WHEN current_player_byes.byes IS NULL THEN 0
    ELSE current_player_byes.byes
  END)
FROM current_players
LEFT JOIN current_player_byes
  ON current_players.id = current_player_byes.id
ORDER BY wins DESC;
\echo 'Created "current_player_standings" view'
