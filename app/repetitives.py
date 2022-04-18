# !bin/env python3
# Author(s): cryptopal85
# Version history: April 07 2022 - Initialising main structure,
#                                - parsing capability for dbmodel and custom SQL queries
# Version history: April 08 2022 - custom input validations
#                                - polish and sanity check
# Version history: April 09 2022 - fixed spotted typos
# Version history: April 13 2022 - fixed the code
# Version history: April 17 2022 - fixed getauthsfilesql
#
# Remarks: Numerous data processing stages need to be repeated within different part of
# the system. Thus, instead of coding those functions each time under the relevant part of the code
# we simply use this module to make the system more portable and understandable. It does
# also allow us to easily reuse these custom functions in 'app.py and authentication.py'
# static HTML views.

### References ###
# Amos, D. (N.D.) Numbers in Python. Available from: https://realpython.com/python-numbers/#integers [Accesssed 18 April 2022].
# Brain Bell (N.D.) Multiple WHERE with AND  OR Operators. Available from: https://www.brainbell.com/tutorials/MySQL/Combining_WHERE_Clauses.htm [Accesses 18 April 2022].
# Flask (N.D.) Define and Acess the Database. Available from: https://flask.palletsprojects.com/en/2.1.x/tutorial/database/ [Accessed 18 April 2022].
# Kapeli (N.D.) Pyhton Format Strings. Available from: https://kapeli.com/cheat_sheets/Python_Format_Strings.docset/Contents/Resources/Documents/index#//dash_ref_Member%20and%20Element%20Access/Entry/Access%20element%20by%20index/0 [Accesss 18 April 2022].
# Python Software Foundation (N.D. A) sqlite3 - DB-API 2.0 interface for SQLite databases. Available from: https://docs.python.org/3.10/library/sqlite3.html#sqlite3.Connection.commit [Accessed 18 April 2022].
# Python Software Foundation (N.D. B) dateime - Basic date and times types. Available from: https://docs.python.org/3.10/library/datetime.html#datetime.datetime.strftime [Accesses 18 April 2022].
# Python Software Foundation (N.D. C) Built-in Types. Available from: https://docs.python.org/3.10/library/stdtypes.html#str.strip [Accessesd 18 April 2022].
# Python Software Foundation (N.D. D) Built-in Functions. Available from: https://docs.python.org/3.10/library/functions.html#isinstance [Accessed 18 April 2022].
# Python Software Foundation (N.D. E) UUID objects according to RFC 4122. Available from: https://docs.python.org/3.10/library/uuid.html#module-uuid [Accesses 18 April 2022].
# Rossum, G. (2013) PEP 8 - Style Guide for Python Code. Available from: https://peps.python.org/pep-0008/#programming-recommendations [Accessed 18 April 2022].
# Smith, A. (N.D.) How to convert a comma-seperated string to a list in Python. Available from: https://www.adamsmith.haus/python/answers/how-to-convert-a-comma-separated-string-to-a-list-in-python [Accessed 18 April 2022].
# Snakify (N.D.) For loop with range. Available from: https://snakify.org/en/lessons/for_loop_range/ [Accessed 18 April 2022].
# SQL Alchemy (N.D.) Query API. Available from: https://docs.sqlalchemy.org/en/14/orm/query.html [Accessed 18 April 2022].
# Tutorialspoint (N.D.) Python MySQL - Cursor Object. Available from: https://www.tutorialspoint.com/python_data_access/python_mysql_cursor_object.htm [Accessed 18 April 2022].


import datetime, uuid, string
# define and access database (Flask, N.D.)
from .db import dbconnectalt
from .dbmodel import DataGroup


##### Parse Data #####

# The following function parses grouplist strings for DataUsers, including
# converting CSV-formatted data into a list (Smith, A., N.D.)


def getauthsfg(glstr):
	# providing string version of object
	# removing whitespaces in digit lists
	aslist = [x.strip(' ') for x in glstr.split(',')]
	return aslist
	

##### SQL Pre-defined Statements #####


# The following function will be used to create custom SQL queries
# where supporting CRUD operations, including fetching the files end users own
# or shared across different groups. It does also meet one of the assignment requirement
# - search capability

def getauthsfilesql(uid, authgroups, ftype, fname=None, fkeytag=None):
	# selecting file meta-data from the database
	sqlselect = """SELECT uuid_hex,filename,keywords_tags,filetype,filecreate,filesize FROM storedfiles WHERE"""
	agsql = "("  # authgroups
	grpcnt = len(authgroups)  # count groups
	for i in range(grpcnt):  # Explained by Snakify (N.D.)
		if i < (grpcnt - 1):
			ag = "authgroups like '%{}%' or ".format(authgroups[i])
			agsql = agsql + ag
		else:
			ag = "authgroups like '%{}' ".format(authgroups[i])
			agsql = agsql + ag
	agsql = agsql + " ))"
	# Search capability by filetype
	if ftype == "any":
		ftsql = "filetype is not null"
	else:
		ftsql = " filetype='{}' ".format(ftype)
		
	# where clause
	sqlwhere = ftsql + " and (fileowner={} or ".format(uid)
	sqlwhere = sqlwhere + agsql
	
	# additional file name or keyword arguments for where clause
	if (len(fname) > 0) and (len(fkeytag) == 0):
		sqlwhere = sqlwhere + "and (filename like '%{}%')".format(fname)
	if (len(fname) == 0) and (len(fkeytag) > 0):
		sqlwhere = sqlwhere + " and (keywords_tags like '%{}%')".format(fkeytag)
	if (len(fname) > 0) and (len(fkeytag) > 0):
		sqlwhere = sqlwhere + " and (filename like '%{}%' or keywords_tags like '%{}%')".format(fname, fkeytag)
		
	# Capability to combine different parts and get combined query
	fullsql = sqlselect + sqlwhere
	return fullsql
	

# The following function fetches binary blobs and mime types.
# It does also  validate if authenticated users are authorised to
# access particular file.
# where clauses and multiple conditions (Brain Bell, N.D.)
def getfiledatasql(uid, authgroups, fileuuid):
	sqlselect = """SELECT filetype,filename,filedata FROM storedfiles"""
	sqlwhere = "where uuid_hex='{}' and ( fileowner={} or".format(fileuuid, uid)
	authgroups = getauthsfg(authgroups)
	agsql = "("
	grpcnt = len(authgroups)
	for i in range(grpcnt):
		if i < (grpcnt - 1):
			ag = "authgroups like '%{}%' or".format(authgroups[i])
			agsql = agsql + ag
		else:
			ag = "authgroups like '%{}%'".format(authgroups[i])
			agsql = agsql + ag
	agsql = agsql + " ))"
	sqlwhere = sqlwhere + agsql
	fullsql = sqlselect + sqlwhere
	return fullsql

	
def testfileownersql(fileuuid):
	if not isinstance(fileuuid, str):
		return None
	if len(fileuuid) != 32:  # number of chars in strings
		return None
	else:
		# https://simple.wikipedia.org/wiki/Hexadecimal
		sqlselect = """SELECT fileowner,filename FROM storedfiles WHERE uuid_hex='{}'""".format(fileuuid)
		return sqlselect
		

# The following function allow modification of file permissions
# only by authorised individual or a validated file owner


def updatesharedgroupssql(grouplist, fileuuid, fileowner):
	asglist = ','.join([str(x) for x in grouplist])
	updgrpsql = """UPDATE storedfiles SET authgroups='{}' WHERE uuid_hex='{}' and fileowner={}""".format(asglist, fileuuid, int(fileowner))
	return updgrpsql


def getfiledeletesql(uid, fileuuid):
	deletesql = """DELETE FROM storedfiles WHERE uuid_hex='{}' and fileowner='{}'""".format(fileuuid, uid)
	return deletesql
	

##### SQL Queries #####

# setting up connection to SQLAlchemy
# that is needed for queries that use customised SQL statements (SQL Alchemy, N.D.)

# The following function leverages connection functions of 'init.py'
def getauthsfiles(dbconlist, appsql):
	try:
		dbhandle = dbconnectalt(dbconlist)
		thiscur = dbhandle.cursor()  # Explained by Tutorialspoint (N.D.)
		thiscur.execute(appsql)
		tuplelist = thiscur.fetchmany(size=15)  # fetch first 15 records
		dbhandle.close()
	except Exception as err:
		return None
	if isinstance(tuplelist, list):
		return tuplelist
	else:
		return None


def getfiledata(dbconlist, filesql):
	try:
		dbhandle = dbconnectalt(dbconlist)
		thiscur = dbhandle.cursor()
		thiscur.execute(filesql)  # fetch file type and binary
		resulttuple = thiscur.fetchone()
		dbhandle.close()
	except Exception as err:
		return None
	if isinstance(resulttuple, tuple):
		return resulttuple  # confirm if it exists
	else:
		return None


def testfileownership(dbconlist, ownersql):
	try:
		dbhandle = dbconnectalt(dbconlist)
		thiscur = dbhandle.cursor()
		thiscur.execute(ownersql)
		resulttuple = thiscur.fetchone()  # fetch file type and binary
		dbhandle.close()
	except Exception as err:
		return None
	return resulttuple  # Explained by Rossum (2013)


def updatesharedgrp(dbconlist, shgrpsql):
	try:
		dbhandle = dbconnectalt(dbconlist)
		thiscur = dbhandle.cursor()
		resultcode = thiscur.execute(shgrpsql)
		dbhandle.commit()  # Explained by Python Software Foundation (N.D. A)
		dbhandle.close() 
	except Exception as err:
		print(err)
		return None
	return resultcode  # Explained by Python Software Foundation (N.D. B)
	

# The following function fetch details of each group end user has authorisation
# fetching all details and moving into temporary container
def getgroupdetails(asglist):
	asgroupdetails = dict()
	for asg in asglist:
		tmplist = []
		grouprecord = DataGroup.query.filter_by(groupid=asg).first()  # Explained by Amos (N.D.)
		if grouprecord is not None:
			tmplist.append(grouprecord.groupname)
			tmplist.append(grouprecord.groupdesc)
			tmplist.append(grouprecord.grouptype)
	return asgroupdetails
	

# The following function is a database insert function to upload files
def newfileupload(dbconlist, upsql, upval):
	try:
		dbhandle = dbconnectalt(dbconlist)
		thiscur = dbhandle.cursor()
		result = thiscur.execute(upsql, upval)
		dbhandle.commit()
		dbhandle.close()
		return result
	except Exception as err:
		print(err)
		return None
		

# The following function is a database delete function to delete files
def deletefilerecord(dbconlist, delsql):
	try:
		dbhandle = dbconnectalt(dbconlist)
		thiscur = dbhandle.cursor()
		result = thiscur.execute(delsql)
		dbhandle.commit()
		dbhandle.close()
		return result
	except Exception as err:
		print(err)
		return None
		

##### DB output processing #####


def newresultsdict(resultlist):
	filemetadict = dict()
	if len(resultlist) > 0:
		for result in resultlist:
			filedate = result[4].strftime("%Y-m%-%d %H:%M:%S")  # Explained by Python Software Foundation (N.D. C)
			if len(result[2]) > 15:
				keytagdisplay = result [2] [:12] + " ..."
			else:
				keytagdisplay = result[2]
			# Converting it to human-friendly file size
			if result[5] > 1000000:  # https://realpython.com/python-numbers/#integers
				fsize = "{} megabytes".format(str(round(float(result[5]/999999.9), 2)))
			elif result[5] > 1000 and result[5] < 1000000:
				fsize = "{} kilobytes".format(str(round(float(result[5]/999.9), 2)))
			else:
				fsize = "{} bytes".format(str(result[5]))
			keydata = "{} {} {} {} {}".format(result[1].strip(), keytagdisplay, filedate, result[3], fsize)
			filemetadict[result[0]] = keydata
	else:
		print("<empty> HTML bla bla")
	return filemetadict


# The following function below sets a mime type for file extension.
def getmimetype(filetype):
	if filetype.lower() == "zip":
		truemime = 'application/zip'
	elif filetype.lower() == "docx":
		truemime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
	elif filetype.lower() == "xls":
		truemime = 'application/vnd.ms-excel'
	elif filetype.lower() == "jpeg":
		truemime = 'image/jpeg'
	elif filetype.lower() == "jpg":
		truemime = 'image/jpeg'
	elif filetype.lower() == "svg":
		truemime = 'image/svg+xml'
	elif filetype.lower() == "pdf":
		truemime = 'application/pdf'
	elif filetype.lower() == "txt":
		truemime = 'text/csv'
	elif filetype.lower() == "csv":
		truemime = 'text/csv'
	else:
		truemime = 'invalid-mimetype'
	return truemime  # return string value

# The following function handle conversion between dictionaries and tuples


def newsharedgroups(shrgrpdict):
	presgrouplist = []
	shrgrpitems = shrgrpdict.items()
	for item in shrgrpitems:
		gid = item[0]
		gname = item[1][0]
		if len(item[1][1]) > 30:
			gdesc = item[1][1][:27] + "..."
		else:
			gdesc = item[1][1]
		gdetails = "{}: {}".format(gname, gdesc)  # Explained by Kapeli (N.D.)
		presgrouplist.append((gid, gdetails))
	return presgrouplist
	


##### static HTML input field check #####

# removing whitespaces around the provided input,
# also detecting if non-allowed chars used in the input field and
# replacing that with 'invalid_input'


def testuserstrps(ustr):
	strpustr = ustr.strip()  # Explained by Python Software Foundation (N.D. C)
	allowlist = string.ascii_letters + string.digits
	for char in strpustr:
		if char not in allowlist:
			# terminate the request and send the provided input for investigation
			defang = "- -" + ustr + "- -"
			return [False, "invalid_input", defang]
	return [True, strpustr]
	


# The following function confirms the radio buttons
# on the static HTML views are used to select files


def testfsradio(rb1, rb2):
	if (not isinstance(rb1, str)) and (not isinstance(rb2, str)):  # Explained by Python Software Foundation (N.D. D)
		msg = "Please repeat the search and do not forget to select one of the available radio buttons"
		return msg
	elif (isinstance(rb1, str)) and (not isinstance(rb2, str)):
		msg = "None of the available radio buttons selected!"
		return msg
	elif (not isinstance(rb1, str)) and (isinstance (rb2, str)):
		msg = "No file selected!"
		return msg
	elif (rb1 == '00000000000000000000000000000000'):
		msg = "Nothing found!"
		return msg
	else:
		return None


def testfschkbx(cblist):
	if len(cblist) == 0:
		msg = "This file won't be share with any groups from now on"
		return msg
	return None
	

# The following function checks if the file has unusual naming patterns
def getfileextension(flupfilename):
	flupext = flupfilename.split('.')[-1]
	return flupext
	

# Check if the selected extension is on the list of available extensions
def testfileextension(flupext, fluptype):
	if flupext.lower() != fluptype.lower():
		msg = "The selected file extension and file type didn't match"
		return msg
	return None
	

# Format the current date and time into MySQL date time convention
def getcurdate():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	

# Create UUID on the server side, then send it to database as hex value
# It can be used in the views and easily converted back and forth
# uuid4 from Python is used due to Privacy concerns (Pyhton Software Foundation, N.D. E)
def getnewuuid():
	hexuuid = uuid.uuid4().hex
	return hexuuid
	

def getuuidstring(hexuuid):
	return str(uuid.UUID(hexuuid))
	

##### ISS DES Logging Patterns #####


def newlogheader(ld, td, cd, uid=0):  # Default value is 0
	levelist = ['debug', 'info', 'warning', 'error', 'critical']
	typelist = ['ActivityTracking', 'EventOfInterest', 'AnomalousActivity', 'ApplicationError']
	categorylist = ['URLAccess', 'AuthenticationSuccess', 'AuthenticationFailure', 'AuthorizationSuccess', 'AuthorizationFailure', 'AuthorizationChange', 'FileAccess', 'FileCreation', 'DatabaseException', 'ApplicationException']
	logmsgdict = dict()
	logmsgdict['eventlogtime'] = datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
	logmsgdict['level'] = levelist[ld]
	logmsgdict['type'] = typelist[td]
	logmsgdict['category'] = categorylist[cd]
	logmsgdict['userid'] = str(uid)
	return logmsgdict
	

def newlogmsg(lhd, lpl):
	if len(lpl) % 2 != 0:
		payload = ','.join(lpl)
		lpl = ['InvalidPayload', payload]
	# Add the new keys and their values to the dict
	for i in range(0, len(lpl), 2):
		lhd[lpl[i]] = lpl[i + 1]
	return lhd
