Sports Catalog
==================

## Summary
A sports catalog webserver that keeps track of different catalog items and displays them on a webpage. It also allows user to login and add, update or delete items.

## Instructions
Clone the package

Run vagrant
```
cd vagrant
vagrant up
vagrant ssh
```

Inside vagrant shell

initialize database
```
cd /vagrant/catalog
python database_setup.py
```

Populate database with dummy data
```
python populate_catalog_with_dummy_data.py
```

Start the web server
```
python project.py
```

Launch webpage
```
Open a browser with URL http://localhost:5000/
```

## Files
####`project.py`
Main Flask application file that initializes the webserver and takes care of different http requests

####`database_setup.py`
Python module that initializes database

####`populate_catalog_with_dummy_data.py`
Python module that populates database with dummy data

## Database
The project uses three tables

#### Tables
**`User`** - Stores user id, user name, user email and user picture
```
 id | name | email | picture
----+------+-------+---------
```

**`Category`** - Stores category id, name and user id
```
 id | name | user id
----+------+---------
```

**`Item`** - Stores item id, name, description, image, category id and user id
```
 id | name | description | image | category id | user id
----+------+-------------+-------+-------------+---------
```
