
< Execute As ROOT >

-----------------------------------------------------------------------------------------
-- Go to /www/root
-----------------------------------------------------------------------------------------

cd /var/www

-----------------------------------------------------------------------------------------
-- Clone sources
-----------------------------------------------------------------------------------------

PWD = /var/www
git clone https://github.com/app-generator/flask-boilerplate-dashboard-argon.git dashboard

-----------------------------------------------------------------------------------------
-- Create venv
-----------------------------------------------------------------------------------------

PWD = /var/www
virtualenv --python=python3 dashboard

-----------------------------------------------------------------------------------------
-- Activate venv
-----------------------------------------------------------------------------------------

cd /var/www/dashboard
PWD = /var/www/dashboard
source bin/activate
# check python version: -> Python 3.6.8

-----------------------------------------------------------------------------------------
-- Install modules
-----------------------------------------------------------------------------------------

PWD = /var/www/dashboard
pip install -r requirements-sqlite.txt

-----------------------------------------------------------------------------------------
-- Test the app
-----------------------------------------------------------------------------------------

PWD = /var/www/dashboard
export FLASK_APP=run.py
flask run

-----------------------------------------------------------------------------------------
-- Create /var/www/dashboard/wsgi.py 
-----------------------------------------------------------------------------------------

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
#site.addsitedir('/var/www/dashboard/lib/python3.6/site-packages')

#sys.path.append('/var/www/dashboard')
#sys.path.append('/var/www/dashboard/app')

activate_this = '/var/www/dashboard/bin/activate_this.py'

with open(activate_this) as file_:
       exec(file_.read(), dict(__file__=activate_this))

#sys.path.insert(0, '/var/www/dashboard/')
#sys.path.insert(0, '/var/www/dashboard/app')
#sys.path.insert(0, '/var/www/dashboard/lib')
#sys.path.insert(0, '/var/www/dashboard/bin')

from os import environ
from sys import exit

from config import config_dict
from app import create_app, db

get_config_mode = environ.get('APPSEED_CONFIG_MODE', 'Debug')

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid APPSEED_CONFIG_MODE environment variable entry.')

application = create_app(config_mode)

-----------------------------------------------------------------------------------------
-- Edit Apache cfg: /etc/httpd/conf/httpd.conf  
-----------------------------------------------------------------------------------------

<VirtualHost *:80>

     ServerName localhost

     WSGIDaemonProcess dashboard user=apache group=apache threads=2

     WSGIScriptAlias / /var/www/dashboard/wsgi.py

     <Directory /var/www/dashboard>
         Require all granted
     </Directory>

 </VirtualHost>

-----------------------------------------------------------------------------------------
-- Start the server  
-----------------------------------------------------------------------------------------

sudo service httpd restart

Error in logs:

```bash

[Sat Nov 09 12:58:45.666933 2019] [:error] [pid 19409] [client ::1:48684] mod_wsgi (pid=19409): Target WSGI script '/var/www/dashboard/wsgi.py' cannot be loaded as Python module.
[Sat Nov 09 12:58:45.666970 2019] [:error] [pid 19409] [client ::1:48684] mod_wsgi (pid=19409): Exception occurred processing WSGI script '/var/www/dashboard/wsgi.py'.
[Sat Nov 09 12:58:45.666995 2019] [:error] [pid 19409] [client ::1:48684] Traceback (most recent call last):
[Sat Nov 09 12:58:45.667014 2019] [:error] [pid 19409] [client ::1:48684]   File "/var/www/dashboard/wsgi.py", line 32, in <module>
[Sat Nov 09 12:58:45.667081 2019] [:error] [pid 19409] [client ::1:48684]     application = create_app(config_mode)
[Sat Nov 09 12:58:45.667091 2019] [:error] [pid 19409] [client ::1:48684]   File "/var/www/dashboard/app/__init__.py", line 77, in create_app
[Sat Nov 09 12:58:45.667144 2019] [:error] [pid 19409] [client ::1:48684]     register_blueprints(app)
[Sat Nov 09 12:58:45.667154 2019] [:error] [pid 19409] [client ::1:48684]   File "/var/www/dashboard/app/__init__.py", line 24, in register_blueprints
[Sat Nov 09 12:58:45.667171 2019] [:error] [pid 19409] [client ::1:48684]     module = import_module('app.{}.routes'.format(module_name))
[Sat Nov 09 12:58:45.667179 2019] [:error] [pid 19409] [client ::1:48684]   File "/usr/lib64/python2.7/importlib/__init__.py", line 37, in import_module
[Sat Nov 09 12:58:45.667232 2019] [:error] [pid 19409] [client ::1:48684]     __import__(name)
[Sat Nov 09 12:58:45.667242 2019] [:error] [pid 19409] [client ::1:48684]   File "/var/www/dashboard/app/base/routes.py", line 8, in <module>
[Sat Nov 09 12:58:45.667298 2019] [:error] [pid 19409] [client ::1:48684]     from bcrypt import checkpw
[Sat Nov 09 12:58:45.667308 2019] [:error] [pid 19409] [client ::1:48684]   File "/var/www/dashboard/lib/python3.6/site-packages/bcrypt/__init__.py", line 25, in <module>
[Sat Nov 09 12:58:45.667372 2019] [:error] [pid 19409] [client ::1:48684]     from . import _bcrypt
[Sat Nov 09 12:58:45.667390 2019] [:error] [pid 19409] [client ::1:48684] ImportError: cannot import name _bcrypt
```

-----------------------------------------------
The problem is reported on many forums:

https://github.com/dhamaniasad/py-bcrypt/issues/7
https://stackoverflow.com/questions/34974088/failed-to-install-bcrypt-python

-----------------------------------------------
Patch: replace bcrypt with [passlib](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)


-----------------------------------------------
New Issue: Write permissions

    return dialect.connect(*cargs, **cparams)
  File "/var/www/dashboard/lib/python3.6/site-packages/sqlalchemy/engine/default.py", line 481,
    return self.dbapi.connect(*cargs, **cparams)
OperationalError: (sqlite3.OperationalError) unable to open database file
(Background on this error at: http://sqlalche.me/e/e3q8)

Possible patches: 
1. chwon apache:apache on the directory tree 
2. Add new write in the http.conf to allow write for logs & dbms 
 
