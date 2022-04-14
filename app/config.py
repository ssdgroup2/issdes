# !bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising app context
#
# Remarks: app.py is a main block that will be used routing the requests such as

# from flask.app import Flask
from os import environ

SECRET_KEY = environ.get('SECRET_KEY')