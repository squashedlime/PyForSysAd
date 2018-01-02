#!/usr/bin/env python

import os, sys, fnmatch, time
from itertools import islice

class Logs(object):

    """
    martin.holloway@ongame.com
    Check Path exists, file access time, file size and parse file for destIP to find Indexer
    File access time not older than five mins, File size > 100 bytes
     1. splunkd installed but not configured == path missing
     2. Path exists, file access time for metric.log does not change
     3. File size too small 
     4. no destIP in metric.log or incorrect destIP
     5. Look for connect_done
    """

    def __init__(self,debug):
        
        self.logFilePath = "/opt/splunkforwarder/var/log/splunk/"
        self.fileName = "metrics.log"
        self.minsize = 100
	self.maxsize = 536870912 #500mb
	self.DEBUG = debug
	self.stringmatch = "destIp"
	self.stringmatch1 = "connect_done"
	self.ip=""

    def __checkFileSize(self):

            sizeinfo = os.stat(self.logFilePath + self.fileName)
            if self.DEBUG:
                    print "File size(bytes):" + str(sizeinfo.st_size)
            if (sizeinfo.st_size > self.minsize) and (sizeinfo.st_size < self.maxsize):
                        return True
            else:
		if self.DEBUG:
			print "Log too big"   
                return False

    def __checkFileAccesTime(self):

        stat = os.stat(self.logFilePath + self.fileName)
        fileModTime = stat.st_mtime
	now = time.time()
	fiveMins = 300

	if (now - fileModTime) > fiveMins:
	    if self.DEBUG:
	    	print "True - More than 5 mins"
	    return True
	else:
	    if self.DEBUG:
	    	print "False - Less than 5 mins"
	    return False

    def __checkDirExsists(self):

        return os.path.exists(self.logFilePath)

    def __parseLog(self):

        if self.__checkFileSize:#File not too small or too big
	    f = open(self.logFilePath + self.fileName,'r')
	    for line in islice(f,1000000):
		if self.stringmatch in line:
		    y = line.split()
		    for x in y:
			x = str(x)
			if x.startswith(self.stringmatch):
			    x = x.split('=')
			    self.ip = x[1].strip(',')
		    return True	
		elif self.stringmatch1 in line:
		    if self.DEBUG:
			print "OUTPUT: %s"%line
		    return True
 	else:
		if self.DEBUG:
			print "False: file too big"
		return False

    def checkSplunk(self):
	#error 1 = no path 2 = File access time 3. connect_done 0 = OK

	error = 0
	path = self.__checkDirExsists()

	if not path:
	    error = 1
	    print "1"
	    sys.exit(0)

	else:
	    accessTime = self.__checkFileAccesTime()
	    size = self.__checkFileSize()
	    parse = self.__parseLog()
	if accessTime:
	    error = 2
	    
	elif not parse:
	    error = 3
	else:
	    error=0
	if self.DEBUG:
	    print "destIp:%s"%self.ip
	print str(error)


def main():

    x = Logs(False)
    x.checkSplunk()

if __name__=="__main__":

    main()
