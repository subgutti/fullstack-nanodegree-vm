#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def createTournament():
    """Creates a new tournament."""
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO tournament (name) VALUES (%s)",
              ("tournament%d" % random.randint(0, 1000),))
    conn.commit()
    conn.close()


def getCurrentTournament():
    """Returns the current tournament id"""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM tournament ORDER BY created_time DESC;")
    tournament_id = c.fetchone()
    conn.close()
    return tournament_id


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) from current_players;")
    players_count = c.fetchone()
    conn.close()
    return players_count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (name, tournament_id) VALUES (%s, %s)",
              (name, getCurrentTournament()))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        byes: the number of matches the player got bye
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM current_player_standings;")
    player_standings_list = c.fetchall()
    conn.close()
    return player_standings_list


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO matches (tournament_id, winner, loser)"
              "VALUES (%s, %s, %s)",
              (getCurrentTournament(), winner, loser,))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Each player appears exactly once in the pairings.  Each player is paired
    with another player with an equal or nearly-equal win record, that is,
    a player adjacent to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    player_standings = playerStandings()
    index = 0
    matches = []
    if len(player_standings) % 2 == 0:
        # For even number of players in tournament generate
        # matches/pairings directly
        matches = generateMatches(player_standings)
    else:
        # For odd number of players in tournament
        # 1. Move the player eligible for bye to the end of list
        # 2. Generate matches/parirings for remaining players
        #    (ignore the last one)
        # 3. Add the bye match for the last player
        player_standings = movePlayerEligibleForByeToEnd(player_standings)
        matches = generateMatches(player_standings[:-1])
        bye_match = (player_standings[-1][0],
                     player_standings[-1][1],
                     None,
                     None)
        matches.append(bye_match)

    return matches


def generateMatches(player_standings):
    """Pairs the players for the next round of a match.

    The total number of players should be even.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    if len(player_standings) % 2 != 0:
        raise ValueError("Total players should be even")

    matches = []
    index = 0
    while index < len(player_standings):
        match = (player_standings[index][0],
                 player_standings[index][1],
                 player_standings[index + 1][0],
                 player_standings[index + 1][1])
        matches.append(match)
        index = index + 2  # as two players are added to a match
    return matches


def movePlayerEligibleForByeToEnd(player_standings):
    """ Sort the list by moving the player elligible for bye at the end

    Each player is elligible for only one bye. Inorder to identify the player
    elligible for bye, traverse the list from bottom and identify the player
    by checking their 'byes' value in 'current_player_standings' view. If
    the value is 0 then the player is elligible for bye.

    Returns:
      A sorted list of player standings with the player elligible for
      bye at the end
    """
    index = last_index = len(player_standings) - 1

    if player_standings[index][4] == 0:
        return player_standings
    else:
        while (index > 0):
            if player_standings[index][4] == 0:
                player_standings.insert(
                    last_index, player_standings.pop(index))
                break
            index = index - 1

    return player_standings
