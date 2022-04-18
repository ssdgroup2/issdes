# !bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising main structure (Flask, N.D. A; Flask, N.D. B)
#                             
#                  April 12 2022 - re-structring - fixed a logic flaw
#
### References ###
# Flask (N.D. A) The Application Context. Available from: https://flask.palletsprojects.com/en/2.1.x/appcontext/ [Accessed 18 April 2022].
# Flask (N.D. B) Application Factories. Available from: https://flask.palletsprojects.com/en/2.1.x/patterns/appfactories/ [Accessed 18 April 2022].



from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from os import environ

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
