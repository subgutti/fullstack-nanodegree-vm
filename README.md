Tournament Planner
==================

## Summary
Python module that uses the PostgreSQL database to keep track of players and matches a game tournament and will use the swiss system for pairing up player in each round.

## Instructions
To verify
```
python tournament/tournament_test.py
```

## Files
####`tournament.sql`
PostgreSQL code that creates the `tournament` database with the required tables and views

####`tournament.py`
Python module that interacts with the PostgreSQL database and provides helpful methods for interaction with database

####`tournament_test.py`
Test cases for `tournament.py` methods

## Database
The project uses two tables and a view to meet the requirements

#### Tables
**`players`** - Stores player ID and name
```
 id | name
----+-----
```

**`matches`** - Stores winner and loser player id
```
 winner | loser
--------+-------
```

#### Views
**_`player_standings`_** - A view showing each player's standings.
Relies on `players` and `matches` tables
```
 id  | name | wins | matches
-----+------+------+---------
```
