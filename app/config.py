#!bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising app context
#
# Remarks: app.py is a main block that will be used routing the requests such as

# from flask.app import Flask
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = environ.get('SECRET_KEY')