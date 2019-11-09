
import os
import sys
import site

# dynamic discover
activate_this = '/var/www/dashboard/bin/activate_this.py'
with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/var/www/dashboard/lib/python3.6/site-packages')

sys.path.insert(0, '/var/www/dashboard/')
sys.path.insert(0, '/var/www/dashboard/app')
sys.path.insert(0, '/var/www/dashboard/lib')
sys.path.insert(0, '/var/www/dashboard/bin')

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

