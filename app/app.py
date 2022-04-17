# !bin/env python3
# Author(s): cryptopal85
# Version history: April 05 2022 - Initialising main structure
#                                - building authentication - preparing routing and html templates
#                  April 06 2022 - building CRUD functionalities
#                  April 07 2022 - building CRUD functionalities and polishing
#                  April 12 2022 - fixing routes and views
#                  April 15 2022 - fixing upload function and routes
#                  April 16 2022 - fixing share function and routes
#
# Remarks: app.py is a main block that will be used routing the requests such as
# viewing, sharing, uploading files, etc. to appropriate URLs.
# End-user facing requests, including input forms will mostly done within relevant html templates.

import re
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
from markupsafe import escape
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from os import environ, path
from .db import db, getconnectiondata, newdburi
from .dbmodel import DataUser, User, DataGroup
import io
# other custom functions and module classes
from .repetitives import getauthsfg, getauthsfilesql, getauthsfiles, newresultsdict, getfiledatasql, getfiledata, getmimetype, testfileownersql, testfileownership, getgroupdetails, newsharedgroups, updatesharedgroupssql, updatesharedgrp, testfsradio, getfileextension, testfileextension, getcurdate, getnewuuid, newfileupload, getfiledeletesql, deletefilerecord, newlogmsg, newlogheader


app = Blueprint('app', __name__)


##### Authentication #####


# Landing page for unauthenticated users, login block shown here
@app.route('/')
def index():
	return render_template('index.html')

# This is the traditional home page for the authenticated users
# It will validate login and will route to the other variant of the same page once authentication confirmed.
# The second variant of the same page then will also list authorised groups (group membership) and logged user details.
# Failed authentication will redirect to the unauthenticated users landing page (index.html)
# Flask has a built-in method called login_required where protects access to routes that including login_required.
# This method is one of the other safeguard that mitigates major part of the OWASP broken authentication threats.
#
# Flask-login get_id returns the authenticated individual's numeric ID
# which can be used to extract attributes from classes like DataUser, User, etc. (needs to be clarified)


@app.route('/home')
@login_required
def presenthome():
	print("inside presenthome")
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
	if thisdatauser:
		dname = thisdatauser.userdisplayname
		asglist = thisdatauser.authgroups
		if asglist is None:
			asglist = "No group membership found"
	return render_template('home-logged.html', displayname=dname, grouplist=asglist)


##### File Operations #####

# The app's search and download functionality handled here
# It will be the main block for authorised users when interacting with files
# Several file types will be presented to users
# Users will able to carry certain operations like downloading, sharing, deleting, etc.


@app.route('/search-download-1', methods=['GET'])
@login_required
def presentview():
	print("inside present view")
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
	if thisdatauser:
		asglist = thisdatauser.authgroups
		duaid = thisdatauser.useraccessid
		if asglist is None:
			flash("The user {} is not member of any authorised groups. Please contact the ISS ground centre to get support".format(duaid))
			asglist = "** No group membership **"
	return render_template('search.html', grouplist=asglist, aid=duaid)

	
@app.route('/search-download-1', methods=['POST'])
@login_required
def presentview2():
	print("inside present view2")
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
	if thisdatauser:
		thisaid = thisdatauser.useraccessid
		asglist = thisdatauser.authgroups
		if asglist is None:
			flash("The user {} is not member of any authorised groups. Please contact the ISS ground centre to get support").format(thisaid)
			duserfilegroups = ['122', '124']  # a workaround for users with no membership
		else:
			duserfilegroups = getauthsfg(asglist)
		# Use the authorisation-based function on the SQL userid and groups
		# Update SQL based on search queries
		sftype = request.form.get('selectedfiletype')
		sfname = request.form.get('filename')
		skeytag = request.form.get('keyword-tag')
		authsfilesql = getauthsfilesql(uid, duserfilegroups, sftype, sfname, skeytag)
		if len(sfname) == 0:
			sfname = "any file name"
		if len(skeytag) == 0:
			skeytag = "any keywords"
		# we need to process the SQL produced above - initialise db connection
		dbcondata = getconnectiondata()
		resultslist = getauthsfiles(dbcondata, authsfilesql)
		if resultslist is not None and len(resultslist) > 0:
			# let's convert the tuples into a dictionary - what are the tuples? https://www.w3schools.com/python/python_tuples.asp
			authsdict = newresultsdict(resultslist)
		else:
			authsdict = dict()
			authsdict['00000000000000000000000000000000'] = "No files found for this search: {}".format(sftype)
	return render_template('view2.html', asfiledict=authsdict, aid=thisaid, grouplist=asglist, searchfname=sfname, searchkeytag=skeytag, searchtype=sftype)
	
	
# The app's upload functionality handled here
# Metadata of the uploaded files will include current time and unique ID of authenticated users
# Although it depends to available deployment models, this data will be held on the server side to avoid tampering
#
# The unusual URL routing activities, file-up-2 sending data to file-up allows to create potential secmon rules
# I.E., malicious exploring activities in the app once authenticated with a valid credentials
# numerous URL discovery requests based on the existing naming conventions


@app.route('/file-up-2', methods=['GET'])
@login_required
def presentupload():
	print("inside presentupload /file-up-2")
	return render_template('upload.html')

# The main route used to handle actual file uploads, content validations, suspicious contents
# and authenticated user's id identification


@app.route('/file-up-1', methods=['POST'])
@login_required
def processupload():
	if current_user.is_authenticated:
		uid = current_user.get_id()
		# collecting data here for logging
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
	if thisdatauser:
		thisaid = thisdatauser.useraccessid
	# if no input given/empty
	newfile = request.files['fileup']
	if newfile.filename == '':
		errmsg = "No file selection detected"
		flash(errmsg)
		return redirect(url_for('app.presentupload'))
	# Leading file paths can be removed with Werkzeug - OWASP explanation below:
	# https://owasp.org/www-community/attacks/Path_Traversal
	newfilesecname = secure_filename(newfile.filename)
	flupkeytag = request.form.get('fileup-keyword-tag')
	# Trim keywords while storing files - 254 char is a hard limit
	if len(flupkeytag) > 254:
		flupkeytag = flupkeytag[:254]
	# Remove potentially malicious html tags
	flupkeytag = escape(flupkeytag)
	fluptype = request.form.get('uploadedfiletype')
	if len(fluptype) == 0:
		errmsg = "Use the dropdown menu to select one of the available file types"
		flash(errmsg)
		return redirect(url_for('app.presentupload'))
	flupmimetest = getmimetype(fluptype)
	if flupmimetest == 'invalid-mimetype':
		print("sec0001: Suspicious mimetype detected {} ".format("- -" + flupmimetest + "- -"))
		errmsg = "Use the dropdown menu to select one of the available file types"
		flash(errmsg)
		return redirect(url_for('app.presentupload'))
	# Validate the extension extracted from file is a selected extension type
	flupext = getfileextension(newfilesecname)
	errmsg = testfileextension(flupext, fluptype)
	if errmsg is not None:
		flash(errmsg)
		return redirect(url_for('app.presentupload'))
	# Input Testing
	filedata = newfile.stream.read()  # byte stream
	filesize = len(filedata)
	if filesize > 50000000:
		errmsg = "Filesize is bigger than defined limits - 45mb"
		flash(errmsg)
		return redirect(url_for('app.presentupload'))
	# move metadata into database
	filecreate = getcurdate()
	fileuuid = getnewuuid()
	uploadsql = """INSERT INTO storedfiles(uuid_hex,filename,filetype,filedata,fileowner,filecreate,filesize,keywords_tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
	valuetuple = (fileuuid, newfilesecname, fluptype, filedata, uid, filecreate, filesize, flupkeytag)
	dbcondata = getconnectiondata()
	resultslist = newfileupload(dbcondata, uploadsql, valuetuple)
	# custom logging events
	payloadlist = ['AccessID', thisaid, 'FileName', newfilesecname, 'FIleUUId', fileuuid, 'FileCreate', filecreate]
	logmsgdict = newlogheader(2, 1, 7, str(uid))
	logmsg = newlogmsg(logmsgdict, payloadlist)
	current_app.logger.warning(logmsg)
	return render_template('upload-notification.html', fname=newfilesecname, aid=thisaid)


##### Other Operations #####

# File Share
@app.route('/share-1', methods=['GET'])
@login_required
def presentshare():
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
	if thisdatauser:
		thisaid = thisdatauser.useraccessid
		asglist = thisdatauser.authgroups
		if asglist is None:
			usergroupdict = dict()
		else:
			asglist = getauthsfg(asglist)
			usergroupdict = getgroupdetails(asglist)
		fileid = request.args.get('ukn')
		# check if user at least member of one group
		if len(usergroupdict) > 0:
			thispresgroups = newsharedgroups(usergroupdict)
		else:
			flash("the account {} is not member of any authorised groups. Contact the ISS ground centre for getting support".format(thisaid))
			return redirect(url_for('app.presentview'))
		if fileid is None:
			errmsg = "No file selected, return to the 'Search' page for sharing a file"
			flash(errmsg)
	return render_template('share.html', presgroups=thispresgroups, ukn=fileid)

	
@app.route('/share-2', methods=['POST'])
@login_required
def processshare():
	if current_user.is_authenticated:
		uid = current_user.get_id()
	checkshared = request.form.getlist('sharedgroups')
	fileid = request.form.get('ukn2')
	updategrpsql = updatesharedgroupssql(checkshared, fileid, uid)
	dbcondata = getconnectiondata()
	updatesharedgrp(dbcondata, updategrpsql)
	return render_template('share-notification.html')


##### Download #####
@app.route('/share-download-2', methods=['POST'])
@login_required
def getdownload():
	# We need to confirm the state of radio buttons whether they are checked or not
	# since we mostly avoid client side javascripts, this can be done on the server side
	print("inside search-download-2")
	fileuuid = request.form.get('fileselection')
	selaction = request.form.get('actionrequest')
	# Input validation goes here
	errmsg = testfsradio(fileuuid, selaction)
	if errmsg is not None:
		flash(errmsg)
		return redirect(url_for('app.presentview'))
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
		asglist = thisdatauser.authgroups
		aid = thisdatauser.useraccessid
		if asglist is None:
			flash("The user {} is not member of any authorised groups. Please contact the ISS ground centre to get support".format(aid))
			asglist = "122,124"
			
		# check if the authenticated user is the current owner of the uploaded file
		# otherwise, treat it like an error
		if selaction == "sharefile" or selaction == "deletefile":
			tfosql = testfileownersql(fileuuid)
			dbcondata = getconnectiondata()
			tforesult = testfileownership(dbcondata, tfosql)
			if int(tforesult[0]) != int(uid):
				errmsg = "Account {} not the current owner of file {}".format(aid, tforesult[1])
				flash(errmsg)
				return redirect(request.referrer)
			else:
				if selaction == "sharefile":
					return redirect(url_for('app.presentshare', ukn=fileuuid))
				if selaction == "deletefile":
					return redirect(url_for('app.delete', ukn=fileuuid))
		else:
			# re-run the check above one more time to detect IDOR attacks
			# https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html
			print("Confirm if UID {} , in these groups {}, authorised for this {}".format(uid, asglist, fileuuid))
			thissql = getfiledatasql(uid, asglist, fileuuid)
			dbcondata = getconnectiondata()
			thisfilereq = getfiledata(dbcondata, thissql)
			if thisfilereq is None:
				return render_template('downloadfailure.html', tempprint=thissql)
			else:
				filetype = thisfilereq[0]
				filename = thisfilereq[1]
				fileblob = io.BytesIO(thisfilereq[2])  # Converting and preparing the byte array to send
				newmime = getmimetype(filetype)
				# log the executed action here
				payloadlist = ['AccessID', aid, 'FileName', filename, 'FileType', filetype]
				logmsgdict = newlogheader(1, 1, 6, str(uid))
				logmsg = newlogmsg(logmsgdict, payloadlist)
				current_app.logger.info(logmsg)
				return send_file(fileblob, as_attachment=True, download_name=filename, mimetype=newmime)
	# Unauthenticated Users
	else:
		return render_template('index.html')


# Avoid potential IDOR attacks and not allow 'GET' method
@app.route('/search-download-2', methods=['GET'])
def presentdlredirect():
	return render_template('index.html')


##### Delete #####
@app.route('/delete-2', methods=['GET'])
@login_required
def delete():
	print("inside delete method")
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
		thisaid = thisdatauser.useraccessid
		# fetch details
		fileid = request.args.get('ukn')
		delsql = getfiledeletesql(uid, fileid)
		dbcondata = getconnectiondata()
		results = deletefilerecord(dbcondata, delsql)
		# log the executed action here
		payloadlist = ['AccessID', thisaid, 'FileId', fileid, 'ActivityDetail', 'SuccessfulFileDeletion']
		logmsgdict = newlogheader(1, 1, 6, str(uid))
		logmsg = newlogmsg(logmsgdict, payloadlist)
		current_app.logger.info(logmsg)
		return render_template('delete-notification.html', aid=thisaid)


##### Profile Management #####
# The application blocks below allows users to see their PII/SPI data held within the ISS DES,
# including a form to change their current password


@app.route('/profile-1', methods=['GET'])
@login_required
def showuser():
	print("inside show user")
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
	if thisdatauser:
		userdisplay = dict()
		userdisplay['Access ID'] = thisdatauser.useraccessid
		userdisplay['List of Group Memberships'] = thisdatauser.authgroups
		userdisplay['Space Agency Membership'] = thisdatauser.useragency
		userdisplay['First Name'] = thisdatauser.userforename
		userdisplay['Surname'] = thisdatauser.usersurname
	print(userdisplay)
	return render_template('user.html', udict=userdisplay)


@app.route('/profile-2', methods=['POST'])
@login_required
def updateuser():
	if current_user.is_authenticated:
		uid = current_user.get_id()
		thisdatauser = DataUser.query.filter_by(userid=uid).first()
	if thisdatauser:
		userdisplay = dict()
		userdisplay['Access ID'] = thisdatauser.useraccessid
		userdisplay['List of Group Memberships'] = thisdatauser.authgroups
		userdisplay['Space Agency Membership'] = thisdatauser.useragency
		userdisplay['First Name'] = thisdatauser.userforename
		userdisplay['Surname'] = thisdatauser.usersurname

	thisaccessid = request.form.get('aid')
	# validate session aid (access ID)
	oldpassword = request.form.get('pwd')
	newpassword = request.form.get('pwd2')
	print(oldpassword)
	print(newpassword)
	flash("The account {} password has been changed successfully".format(thisaccessid))
	return render_template('user.html', udict=userdisplay)