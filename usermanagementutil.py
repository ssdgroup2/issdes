# !bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising main structure
#                  April 13 2022 - fixed syntax errors
#
# Remarks: Assuming this CLI-based tool will be used for administrating users
# alongside with 'makeissdesuser.py'. This modude is a support module
# mostly aiding the main tool.


import datetime, mysql.connector
from werkzeug.security import generate_password_hash

# connecting to the database


def dbconnect(dbhost, dbuser, dbcred, dbname):
	try:
		dbh = mysql.connector.connect(
			host=dbhost,
			user=dbuser,
			password=dbcred,
			database=dbname
		)
		return dbh
	except mysql.connector.Error as err:
		print(err)
		return None
		

# extracting and formatting current date and time
def getcurdate():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	

# Performing basic length check on the string for the password
# storing only hashed values in the database
def checkgenpasswd(pwd):
	if len(pwd) < 10:
		print('Password needs to longer than 10 char')
		return None
	else:
		shpwd = generate_password_hash(pwd, method='pbkdf2:sha256', salt_length=16)
		return shpwd
		

# Checking here if the tool administrators used valid space agency names/groups
def checkuseragency(agency):
	agencylist = ['europe', 'us', 'canada', 'japan', 'russia']
	if agency.lower() not in agencylist:
		return int(99)
	if agency.lower() == 'europe':
		return int(14)
	elif agency.lower() == 'us':
		return int(11)
	elif agency.lower() == 'canada':
		return int(19)
	elif agency.lower() == 'japan':
		return int(15)
	elif agency.lower() == 'russia':
		return int(12)
	else:
		return(99)