# !bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising main structure
#                                - https://flask.palletsprojects.com/en/2.1.x/appcontext/
#                                - https://flask.palletsprojects.com/en/2.1.x/patterns/appfactories/
#                  April 12 2022 - re-structring
#                  April 15 2022 - moving db-related codes under db.py module


from flask import Flask
from os import environ
from flask_login import LoginManager
from datetime import timedelta
import logging
from .db import getconnectiondata
from .db import newdburi
from .db import db


def create_app():
	app = Flask(__name__)
	connlist = getconnectiondata()
	dburi = newdburi(connlist)
	app.config.from_pyfile('config.py')
	app.config['SQLALCHEMY_DATABASE_URI'] = dburi
	app.config['SQLALCHEMY_ECHO'] = False
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=900)
	# get secret key from env file
	app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
	logging.basicConfig(filename='/var/tmp/issdes.log', level=logging.DEBUG)

	# enable SQLAlchemy
	db.init_app(app)

	# enable Flask_login LoginManager
	login_manager = LoginManager()
	login_manager.login_view = 'authentication.login'
	login_manager.init_app(app)
	from .dbmodel import User
	
	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	# import custom functions
	
	# import & register blueprints
	with app.app_context():
		from .authentication import authentication as authentication_blueprint
		app.register_blueprint(authentication_blueprint)
		from .app import app as app_blueprint
		app.register_blueprint(app_blueprint)
		
		return app