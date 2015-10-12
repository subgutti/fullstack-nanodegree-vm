-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you \echoose to use it.
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
	name TEXT NOT NULL CHECK (name <> '')
);
\echo 'Created "players" table'

-- Create the 'matches' table to keep track of matches
CREATE TABLE matches (
	player1 integer NOT NULL,
	player2 integer NOT NULL,
	winner integer NOT NULL,
	loser integer NOT NULL,
	PRIMARY KEY(player1, player2)
);
\echo 'Created "matches" table'
