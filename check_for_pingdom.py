#!/usr/bin/env python
import sys, string, pingdom, urllib, os, subprocess as sub
from optparse import OptionParser

class pingComm(object):
 
    def __init__(self, ipToPing):
        self.ipToPing = ipToPing
        self.pingQuantity = "1"
 
    def pingProc(self):
        pingTest = "ping -c "+ self.pingQuantity + ' ' + self.ipToPing
        process = sub.Popen(pingTest, shell=True, stdout=sub.PIPE)
        process.wait()
        returnCodeTotal = process.returncode
        return returnCodeTotal

def ping():
	ping = pingComm('www.google.com')
        svar = ping.pingProc()
	status = 0
        if svar == 0:
                rep = "Ping to www.google.com: OK\n"
        else:
                rep = "Ping to www.google.com: FAILED\n"
                status = 1
	return rep, status

def main():
	
	parser = OptionParser()
   	parser = OptionParser(conflict_handler="resolve")
    	parser.add_option("-e", "--env", dest="env", help="GIB, ITA, FRA, ESP")
    	parser.add_option("-m", "--ms", dest="res", help="Response Time in ms")
	(opts, args) = parser.parse_args()
	mandatories = ['env', 'res']
    	for m in mandatories:
        	if not opts.__dict__[m]:
            		print "mandatory option is missing\n"
            		parser.print_help()
            		sys.exit(1)

	#Create an array to place the environment specific information
	checkName = []
	checkID = []
	
	#Connection info
	connect = pingdom.PingdomConnection('EMAIL, 'USERNAME', 'PASSWORD')

	#Set env
	env = opts.env
	responseTime = opts.res
	responseTime = int(responseTime)

	#Create a hash of check name and ID
	try:
    		checks = connect.get_all_checks()

	except PingdomError:
		#Connection to pingdom failed checking ping
		x = ping()
		if x[1] != 0:
			print "Connection to Pingdom failed, testing ping... %s Exiting"%x[1]
			sys.exit(2)

	for check in checks:
		if env in str(check):
			checkName.append(check)
                	checkID.append(check.id)
	AllTestPoints = dict(zip(checkName,checkID))

	#Loop through items and count failurestesttest
	alarmString = "Testing 10 ISP's\n"
	statusError = result
	responseError = 0
	pingError = 0
	counter = 0
    	for name, id in AllTestPoints.iteritems():
        	error = 0
        	result = connect.get_raw_check_results(id, 10)
        	for lines in result:
			counter +=1
                	for point, status in lines.iteritems():
                        	if point == "status":
                                	if status != "up":
						alarmString += " Status Number:%d Result: %s\n"%(statusError,status)
                                        	statusError += 1
				if point == "responsetime":
					if int(status) >= responseTime:
						alarmString += ' Resopnse Number:%d Result: %s\n'%(responseError,status)
						responseError += 1

	alarmString += "Number of tests %d \nNumber of Status Errors:%d\nNumber of response times over threshold %d\n"%(counter,statusError, responseError)
	
	alarmString += "Trying to contact google...\n"
	testPing = ping()
	alarmString += testPing[0]
	pingError += testPing[1]

	#All info collected, alarm if needed
	if statusError >= (counter-10) and pingError != 0:
		print "CRITICAL: No connection to Internet\n" + alarmString
		sys.exit(2)
	if responseError >= (counter-10) and pingError != 0:
		print "CRITICAL: probably no connection to internet\n" + alarmString
		sys.exit(2)
	if responseError >= (counter-10) and pingError == 0:
		print "WARNING: problems with internet connectivity\n" + alarmString	
		sys.exit(1)
	else:
		print "Connection to internet OK\n" + alarmString
		sys.exit(0)

if __name__ == "__main__":
    main()
