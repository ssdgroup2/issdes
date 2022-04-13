#!bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialised main structure for the app's authentication
#                                - added several functions and logging patterns
#                  April 12 2022 - fixed routes and views
#                  April 13 2022 - fixed routes and views
#
# Remarks: The 'authentication.py' mainly used to authenticate end users. Input validations such as for a password used Werkzeug lib.
# Flask/login_user mainly responsible for taking care of registration of authenticated end users
# Flask/login_reqired used to protect all views from unauthorised access


from ast import Str
from crypt import methods
import flask, logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from . import db
from . dbmodel import User, DataUser
from . repetitives import testuserstrps, newlogheader, newlogmsg


authentication = Blueprint('authentication', __name__)


# validating  DataUser - User - PasswordHash
def getdatauser(aid):
	duserobj = DataUser.query.filter(DataUser.useraccessid == aid).first()
	return duserobj


def getdatauid(id):
	duserobj = DataUser.query.filter(DataUser.userid == id).first()
	return duserobj


def getauthns(uidint):
	uauthsnobj = User.query.filter(User.id == uidint).first()
	return uauthsnobj

	
def verify_passwd(pwdhash, pwdstr):
	return check_password_hash(pwdhash, pwdstr)
	

# The following function checks access ID (ID on the login page) and password,
# redirects end user to the login page when authentication fails
# ISS DES's login process consist of two main steps, access ID which is known by
# end users and the user id that is stored and not known by end users in database.
# ISS DES uses user id to authenticate end users' password, including having
# capabilities for locking and disabling end users access ID
# When it comes to detection of suspicious activities,  numerous HTTP 302 events 
# in a short time period from the same IP might be indicative of potential
# credential harvesting, password spraying or traditional brute force attacks


@authentication.route('/login', methods=['POST'])
def login_post():
	accessid = request.form.get('accessid')
	formpasswd = request.form.get('passwd')
	# checking access ID length
	if isinstance(accessid, str) and len(accessid) > 0 and len(formpasswd) > 0:
		unametest = testuserstrps(accessid)
		if unametest[0]:
			thisduserobj = getdatauser(accessid)
			# Detecting invalid users
			if thisduserobj is None:
				flash("Please double check your ID, then retry to login. The ISS ground centre is available for support")
				payloadlist = ['URL', '/login', 'HTTPMethod', request.method, 'FailureReason', 'UnknownUser', 'AccessID', accessid]
				logmsgdict = newlogheader(2, 1, 2)
				logmsg = newlogmsg(logmsgdict, payloadlist)
				print(logmsg)
				current_app.logger.warning(logmsg)
				return redirect(url_for('app.index'))
			# Checking password
			pwdchk = False
			if isinstance(thisduserobj.userid, int):
				thisauthsobj = getauthns(thisduserobj.userid)
			if thisauthsobj is not None:
				pwdchk = verify_passwd(thisauthsobj.userpasswd, formpasswd)
			else:
				print("Failed test - DB mulfunction")
				flash("Please double check your password, then retry to login. The ISS ground centre is available for support")
				return redirect(url_for('app.index'))
			if pwdchk:
				login_user(thisauthsobj)
				# Recording successful login attempts
				payloadlist = ['URL', '/login', 'HTTPMethod', request.method, 'SuccessReason', 'ValidCredentialUse', 'AccessID', accessid]
				logmsgdict = newlogheader(1, 0, 1)
				logmsg = newlogmsg(logmsgdict, payloadlist)
				print(logmsg)
				current_app.logger.info(logmsg)
				return redirect(url_for('app.presenthome'))
			else:
				# Failed login - invalid password for valid user
				flash("Please double check your password, then retry to login. The ISS ground centre is available for support")
				payloadlist = ['URL', '/login', 'HTTPMethod', request.method, 'FailureReason', 'InvalidPassword', 'AccessID', accessid]
				logmsgdict = newlogheader(2, 1, 2)
				logmsg = newlogmsg(logmsgdict, payloadlist)
				print(logmsg)
				current_app.logger.warning(logmsg)
				return redirect(url_for('app.index'))
		else:
			# Suspicious username
			flash("Please double check your ID and Password, then retry to login. The ISS ground centre is available for support")
			payloadlist = ['URL', '/login', 'HTTPMethod', request.method, 'FailureReason', 'InvalidInputCharacters', 'AccessID', unametest[2]]
			logmsgdict = newlogheader(2, 2, 2)
			logmsg = newlogmsg(logmsgdict, payloadlist)
			print(logmsg)
			current_app.logger.warning(logmsg)
			return redirect(url_for('app.index'))
			
	else:
		# Checking if both input fields filled-in
		flash("Please double check if both fields filled in, then retry to login. The ISS ground centre is available for support")
		return redirect(url_for('app.index'))
				

# The function below checks the authentication status of end users and route them to the landing page
# showing their display name - if the authentication status negative then redirects to the login page

@authentication.route('/login', methods=['GET'])
def login():
	if current_user.is_authenticated:
		authnsid = current_user.get_id()
		duserobj = getdatauid(authnsid)
		msg = 'already authenticated as {}'.format(duserobj.userdisplayname)
		flash(msg)
		return redirect(url_for('app.presenthome'))
	else:
		return redirect(url_for('app.index'))


# Allow authenticated users to appropriately close their active sessions
@authentication.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	if current_user.is_authenticated:
		authnsid = current_user.get_id()
		duserobj = getdatauid(authnsid)
		msg = 'Logging out access ID {}'.format(duserobj.useraccessid)
		flash(msg)
		logout_user()
		payloadlist = ['URL', '/logout', 'HTTPMethod', request.method, 'AccessID', duserobj.useraccessid]
		logmsgdict = newlogheader(1, 0, 1)
		logmsg = newlogmsg(logmsgdict, payloadlist)
		print(logmsg)
		current_app.logger.info(logmsg)
		return redirect(url_for('app.index'))
	else:
		return redirect(url_for('app.index'))