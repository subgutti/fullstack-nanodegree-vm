Tournament Planner
==================

## Summary
Python module that uses the PostgreSQL database to keep track of players and matches a game tournament and will use the swiss system for pairing up player in each round.

## Instructions
Clone the package

Run vagrant
```
cd vagrant
vagrant up
vagrant ssh
```

Inside vagrant shell, initialize database
```
cd /vagrant
psql -f tournament.sql
```

Verify
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
The project uses two tables and several views to meet the requirements

#### Tables
**`tournament`** - Stores tournamen ID, name and created time stamp
```
 id | name | created_time
----+------+--------------
```

**`players`** - Stores player ID, name and tournament id
```
 id | name
----+-----
```

**`matches`** - Stores tournament id, winner and loser player id
```
 winner | loser
--------+-------
```

#### Views
**_`current_tournament`_** A view showing the current active tournament
Relies on 'tournament' table
```
 id 
----
```

**`current_players`** - A view showing players in the current tournament
Relies on 'tournament' and 'player' tables
```
 id | name
----+-----
```

**`current_matches`** - A view showing matches in the current tournament
Relies on 'tournament and 'matches' table
```
 id | winner | loser
----+--------+-------
```

**`current_player_byes`** - A view showing players bye count in the current tournament
Relies on 'current_matches' view
```
 id | byes
----+-----
```

**_`current_player_standings`_** - A view showing each player's standings in the current tournament
Relies on `current_players`, `current_matches` and `current_player_byes` views
```
 id  | name | wins | matches | byes
-----+------+------+---------+------
```
