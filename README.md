# Scoring Engine

This is a django app made to mimic the behaviour of the
[CCDC](http://www.nationalccdc.org/) scoring engine.

It is under development by members of the Northeastern University CCDC team for
use in our practice sessions.

### Dependencies

- Django v1.9
- dnspython3
- pysmb
- pymssql
- freetds-dev

### Installing
1. Install dependencies:

`apt-get install freetds-dev`

`pip3 install django dnspython3 pysmb pymssql`

2. Setup the sqlite databse

`python3 manage.py migrate`

3. Register Plugins

`python3 manage.py registerplugins`

3. Customize the configuration in `/engine/config.py` and apply the config to
the database with:

`python3 manage.py configure`

4. Start the server

`python3 manage.py runserver`

The Scoring Engine should now be accessable at http://localhost:8000.

### Included Plugins
- DNS
- FTP
- HTTP
- IMAP
- POP3
- SMTP
- More to come...

### Writing Plugins

In this scoring engine, Plugins check the status of Services. Plugins are
configured as modules in `/engine/plugins/`. These modules should include a
`run(options)` method that returns `True` if a service check passed and `False`
otherwise. When configuring a Plugin in the database, it's name should match
the name of the associated module.

### License

This project is open source under the MIT public license. See [license.txt](license.txt).
