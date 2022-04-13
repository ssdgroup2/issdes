# !bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising main structure
#                                - https://flask.palletsprojects.com/en/2.1.x/appcontext/
#                                - https://flask.palletsprojects.com/en/2.1.x/patterns/appfactories/
#                  April 12 2022 - re-structring - fixed a logic flaw


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_login import LoginManager
from datetime import timedelta
import mysql.connector
import logging


# initialise SQLAlchemy
db = SQLAlchemy()


def getconnectiondata():
	condatalist = []
	issdes = environ.get('dbinstance')
	username = environ.get('dbuser')
	cred = environ.get('dbcred')
	host = environ.get('dbhost')
	if not issdes:
		print("Incorrect or missing info: database instance name")
	else:
		condatalist.append(issdes)
	if not username:
		print("Incorrect or missing info: database user name")
	else:
		condatalist.append(username)
	if not cred:
		print("Incorrect or missing info: database credentials")
	else:
		condatalist.append(cred)
	if not host:
		print("Incorrect or missing info: database host information")
	else:
		condatalist.append(host)
	if len(condatalist) != 4:
		print("Incorrect or missing info")
		exit(1)
	else:
		return condatalist
	return False


def newdburi(connlist):
	user = connlist[1]
	pwd = connlist[2]
	host = connlist[3]
	dbinst = connlist[0]
	dburi = "mysql+mysqlconnector://{}:{}@{}:3306/{}".format(user, pwd, host, dbinst)
	return dburi


# Alternative connection driver for MySQL
def dbconnectalt(conlist):
	try:
		dbh = mysql.connector.connect(
			database=conlist[0],
			user=conlist[1],
			password=conlist[2],
			host=conlist[3],
		)
		return dbh
	except Exception as err:
		print(err)
		return None


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
	from .dbmodel import DataUser
	
	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	# import custom functions
	from .repetitives import getauthsfg, getauthsfiles, getauthsfilesql, newresultsdict, getfiledatasql, getmimetype, getfiledata, testuserstrps, testfileownersql, testfileownership, getgroupdetails, newsharedgroups
	
	# import & register blueprints
	with app.app_context():
		from .authentication import authentication as authentication_blueprint
		app.register_blueprint(authentication_blueprint)
		from .app import app as app_blueprint
		app.register_blueprint(app_blueprint)
		
		return app