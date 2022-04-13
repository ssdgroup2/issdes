#!bin/env python3
# Author(s): cryptopal85
# Version history: April 09 2022 - Initialising main structure
#                  April 13 2022 - fixed syntax errors
#
# Remarks:
# https://docs.python.org/3/library/syslog.html
# https://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python

import time, os, datetime, re, json
# external lib for transporting logs
import pysyslogclient

from ast import literal_eval  # for converting string/dictionary

##### Log Operations #####
# The following function will process and put all events on daily basis to a file


def updatesecevent(eventline):
	datestamp = datetime.datetime.now().strftime("%Y%m%d")
	seceventlog = "/var/tmp/secevent-{}.log".format(datestamp)
	relinesplit = re.search('^\w+:\w+:(.*)', eventline)
	if relinesplit is not None:
		loglinestr = relinesplit.group(1)
		loglinedict = literal_eval(loglinestr)
		with open(seceventlog, "a+") as seceventfh:
			json.dump(loglinedict, seceventfh)
			seceventfh.write("\n")
	return

	
def updatehttpevent(eventline):
	# Daily logs
	datestamp = datetime.datetime.now().strftime("%Y%m%d")
	httpeventlong = "/var/tmp/httpevent-{}.log".format(datestamp)
	relinesplit = re.search('^\w+:\w+:(.*)', eventline)
	if relinesplit is not None:
		ncsalogline = relinesplit.group(1)
		with open(httpeventlong, "a+") as httpeventfh:
			httpeventfh.write(ncsalogline + "\n")
	return
	

##### Transferring Logs to the ground centre #####

def newsyslogclient(hostipstr):
	syslogclient = pysyslogclient.SyslogClientRFC3164(hostipstr, 601, proto="TCP")
	return syslogclient

	
def setremotealert(seceventline):
	app = 'issdesalerting'
	logtransport = newsyslogclient('localhost')
	logtransport.log(seceventline, facility=pysyslogclient.FAC_SECURITY, severity=pysyslogclient.SEV_WARNING, program=app, pid=6666)
	logtransport.close()
	return
	

##### Log Even Filtering #####

def testsecevent(seceventline):
	print(seceventline)
	if seceventline.split(':')[0] == "INFO":
		updatesecevent(seceventline)
	else:
		print("latest alert")
		updatesecevent(seceventline)
		setremotealert(seceventline)
	return
	

# filtering events we get from Werkzeug

def filterline(thisline):
	if thisline.startswith('INFO:werkzeug:'):
		updatehttpevent(thisline)
		return
	elif thisline.startswith('WARNING:werkzeug:'):
		updatehttpevent(thisline)
		return
	elif thisline.startswith('ERROR:werkzeug'):
		updatehttpevent(thisline)
		return
	elif thisline.startswith('CRITICAL:werkzeug'):
		updatehttpevent(thisline)
		return
	else:
		testsecevent(thisline)
	return
	

# Realtime monitoring for Flask logging output - uses Generators
# https://docs.python.org/3.10/tutorial/classes.html#generators

def followfile(applog):
	applog.seek(0, os.SEEK_END)
	
	while True:
		thisline = applog.readline()
		if not thisline:
			time.sleep(0.2)
			continue
		yield thisline

		
if __name__ == '__main__':
	applogfile = open("/var/tmp/issdes.log", "r")
	loglines = followfile(applogfile)
	
	for line in loglines:
		filterline(line)