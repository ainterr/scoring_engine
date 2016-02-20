# Scoring Engine

This is a django app made to mimic the behaviour of the
[CCDC](http://www.nationalccdc.org/) scoring engine.

It is under development by members of the Northeastern University CCDC team for
use in our practice sessions.

### Dependencies

- Django v1.9

### Database Schema

Coming Soon...

### Installing
1. Install dependencies:

`pip install django`

2. Setup the sqlite databse

`python manage.py migrate`

3. Register Plugins

`python manage.py registerplugins`

3. Load the configuration into the database (located in `/engine/config.py`)

`python manage.py configure`

4. Run the server

`pthon manage.py runserver`

The Scoring Engine should now be accessable at http://localhost:8000.

### Writing Plugins

In this scoring engine, Plugins check the status of Services. Plugins are
configured as modules in `/engine/plugins/`. These modules should include a
`run(options)` method that returns `True` if a service check passed and `False`
otherwise. When configuring a Plugin in the database, it's name should match
the name of the associated module.

### License

This project is open source under the MIT public license. See license.txt.
