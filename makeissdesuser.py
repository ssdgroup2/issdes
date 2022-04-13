#!bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising main structure
#                                - Setting default group ID creation
#                  April 10 2022 - fixed syntax errors
#
# Remarks: Assuming this CLI-based tool will be used for administrating users
# alongside with 'usermanagementutil.py'.

from werkzeug.security import generate_password_hash
import getpass
import usermanagementutil


# The function below combines the users unique ID created on the database and password given
# by administrators for end users. It does also automatically set fields for account status
# such as 'locked' or 'disabled' state.
#

def newuserauthns(pwd, shpwd, uid):
	print("The current password: {}".format(pwd))
	
	# move given input into the dabase
	regdate = usermanagementutil.getcurdate()
	newusercred = """INSERT into userauthns (id,userpasswd,userlocked,forcepwdchange,activestatus,userregistration) \
		VALUES (%s,%s,%s,%s,%s,%s)"""
	valuestuple = (int(uid), shpwd, 0, 0, 1, regdate)
	print(valuestuple)
	try:
		thisdbh = usermanagementutil.dbconnect('localhost', 'root', 'hNPDP<bg6^^A', 'issdes')
		thiscur = thisdbh.cursor()
		result = thiscur.execute(newusercred, valuestuple)
		thisdbh.commit()
		thisdbh.close()
		return result
	except Exception as err:
		print(err)
		return None
		

def createdatauser(ufn, usn, udn, aid, ua, ag):
	newusersql = """INSERT into datauser (userforename,usersurname,userdisplayname,useraccessid,useragency,authgroups) VALUES (%s,%s,%s,%s,%s,%s)"""
	valuestuple = (ufn, usn, udn, aid, ua, ag)
	try:
		thisdbh = usermanagementutil.dbconnect('localhost', 'root', 'hNPDP<bg6^^A', 'issdes')
		thiscur = thisdbh.cursor()
		result = thiscur.execute(newusersql, valuestuple)
		thisdbh.commit()
		thisdbh.close()
		return result
	except Exception as err:
		print(err)
		return None
		

def getuserid(accessid):
	uidsql = "SELECT userid,useraccessid from datauser WHERE useraccessid='{}'".format(accessid)
	try:
		thisdbh = usermanagementutil.dbconnect('localhost', 'root', 'hNPDP<bg6^^A', 'issdes')
		thiscur = thisdbh.cursor()
		result = thiscur.execute(uidsql)
		# fetch metadata needed to download files
		recordstuple = thiscur.fetchone()
		uid = recordstuple[0]
		aid = recordstuple[1]
		thisdbh.close()
		return uid
	except Exception as err:
		print(err)
		return None
		

def main():
	quit = False
	while (not quit):
	# user data collection and account creation
		print("Creating new ID for ISS DES")
		print("****************************\n")
		print("Starting user data collection")
		userforename = input("User's first name (first, formal one)?:")
		usersurname = input("User's surname (last)?:")
		userdisplayname = input("User's full name, first or first and last")
		print("User's ID will be created based on the following naming convention:\n 2 char code for spance agency \n 3 digits, first initial, 2 digits, last initial")
		useraccessid = input("Access ID for user, XXdddXddx")
		print("Space Agency group membership, Europe,US,Canada,Japan,Russia")
		useragency = input("Space Agency Group:")
		print(usermanagementutil.checkuseragency(useragency))
		if usermanagementutil.checkuseragency(useragency) != 99:
			authgroups = usermanagementutil.checkuseragency(useragency)
		else:
			print("Not valid user agency, must be one of: Europe,US,Canada,Japan,Russia")
			continue
		# move into the db and get user identifier
		nduresult = createdatauser(userforename, usersurname, userdisplayname, useraccessid, useragency, authgroups)
		if nduresult is not None:
			print(dir(nduresult))
		thisuid = getuserid(useraccessid)
		if thisuid is None:
			print("cannot fetch userid for account {}:".format(useraccessid))
			answer = input("terminate and restart? (y/n):")
			if answer[:1].lower() == 'y':
				quit = True
				
		# generating password, using werkzeug.security hashing for salted passwords
		print("Generating new user password for ISS DES")
		pwdcheck = False
		while (not pwdcheck):
			pwd = getpass.getpass(prompt="Enter minimum 10 char password:")
			shpwd = usermanagementutil.checkgenpasswd(pwd)
			if shpwd:
				newuserauthns(pwd, shpwd, thisuid)
				pwdcheck = True
				
		# End of account creation
		answer = input("all data collected, creating user? (y/n):")
		if answer[:1].lower() == 'n':
			quit = True
		

if __name__ == '__main__':
	main()