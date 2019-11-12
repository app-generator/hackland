# Flask CentOS deployment

This page explains how to deploy a [Flask Dashboard](https://github.com/app-generator/flask-boilerplate-dashboard-argon) sandboxed with a virtualenv and served by Apache HTTP server using the `mod_wsgi` module.

## Environment

Software requirements: apache server, mod_wsgi, virtualenv

### Install [Apache](https://httpd.apache.org/) server

```bash
$ sudo yum install httpd
$ 
$ # by default the server is down.
$ sudo systemctl start httpd
```

### Install [mod_wsgi](https://modwsgi.readthedocs.io/)

```bash
$ sudo yum install mod_wsgi
$
$ # restart apache
$ sudo systemctl restart httpd
```

> Test is `mod_wsgi` is properly loaded

```bash
$ sudo httpd -M | grep wsgi
wsgi_module (shared) # <-- the OK response
```

### Install [Virtualenv](https://virtualenv.pypa.io/)

Virtual environments will sandbox the app to run isolated from the global server environment

```bash
$ sudo pip install virtualenv
```

<br />

## Ownership

The apache server is executed under the `apache` user and group. We can check this using the command:

```bash
$ cat /etc/passwd | grep apache
$ apache:x:48:48:Apache:/usr/share/httpd:/sbin/nologin
```

We can see that theuser apache has no shell, for security reasons. In order to have write access to the `/var/www` directory, let's add current user tot the apache group

```bash
$ sudo usermod -a -G apache loader
```

The next step is to allow the authenticated user ( `loader` ) to have write access to the `/var/www` directory

```bash
$ sudo chmod 775 /var/www
```

<br />

##  Clone sources

```bash
$ cd /var/www
$ git clone https://github.com/app-generator/flask-boilerplate-dashboard-argon.git dashboard
$ # the source code is cloned in the dashboard directory
```

<br />

## Create Virtual environment

```bash
$ pwd # check the current working directory
/var/www
$ 
$ # create the virtual env inside dashboard sources
$ virtualenv --python=python3 dashboard
```

<br />

## Activate venv

The modules required by the Flask application should be installed after VENV activation. Like this the whole appliation will run isolated. 

```bash
$ pwd # check the current working directory
/var/www
$ cd /var/www/dashboard
$
$ # activate the VENV
$ source bin/activate
$ 
$ # check the Python version
$ python --version
Python 3.6.8 # something like Python 3.x means we are on the good track
```

<br />

## Install modules for development

In development mode, SQLite database will be used

```bash
$ pwd # check the current working directory
/var/www/dashboard
$ 
$ pip install -r requirements-sqlite.txt
```

<br />

## Edit the application config

Open the file `/var/www/dashboard/`**config.py**

> Edit line to use a file database:

`SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/database.db'`

## Test the app

At this point we need to test if the application is properly installed. For this we need to start it in standalone mode using Flask

```bash
$ pwd # check the current working directory
/var/www/dashboard
$
$ export FLASK_APP=run.py
$ flask run
$ # the app runs on localhost:5000
$
$ # check with lynx
$ lynx localhost:5000
```

> Note: in case when the port 5000 is ocupied by another process, we can start Flask app using a free port:

```bash
$ flask run --port=5001
$ # the app runs on localhost:5001
$
$ # check with lynx
$ lynx localhost:5001
```

<br />

## Link the app with Apache

The Flask application will be executed by Apache using `mod_wsgi` module

<br />

### Create wsgi loader

A new file must be created in the `dashboard` directory.

> File: `/var/www/dashboard/wsgi.py`

```python
#!/usr/bin/env python

import sys
import site

site.addsitedir('/var/www/dashboard/lib/python3.6/site-packages')

sys.path.insert(0, '/var/www/dashboard/')
sys.path.insert(0, '/var/www/dashboard/app')
sys.path.insert(0, '/var/www/dashboard/lib')
sys.path.insert(0, '/var/www/dashboard/bin')

from os import environ
from sys import exit

from config import config_dict
from app import create_app, db

get_config_mode = environ.get('APPSEED_CONFIG_MODE', 'Debug') #Debug, Production

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid APPSEED_CONFIG_MODE environment variable entry.')

application = create_app(config_mode)
```

### Edit Apache configuration  

> File: `/etc/httpd/conf/httpd.conf`  

```xml

<VirtualHost *:80>

    ServerName localhost

    WSGIDaemonProcess dashboard user=apache group=apache threads=2

    WSGIScriptAlias / /var/www/dashboard/wsgi.py

    <Directory /var/www/dashboard>
        Require all granted
    </Directory>

</VirtualHost>

```

<br />

## Update ownership

More information in this article: [Apache permissions, MKDir fail](https://stackoverflow.com/questions/5165183/apache-permissions-php-file-create-mkdir-fail)

```bash
$ sudo chown apache:apache -R /var/www/dashboard
$ sudo chmod 0750 -R /var/www/dashboard
```

<br />

## Start / restart the server

```bash
$ sudo service httpd restart
```
