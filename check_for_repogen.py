#!/usr/bin/env python

import os, sys, datetime, socket,fnmatch, time, logging
from optparse import OptionParser
"""
A monitoring script that compares the reports in reports_list.txt with the actual reports in /opt/report_generator/done_ftp/
use -v for verbose information and -d for DWH

"""
class ReportGenerator(object):

        def __init__(self,Debug,dwh):

                #self.pathToFile = "/tmp/reports_list.txt"
                self.pathToFile = "/opt/ongame/report_generator/docs/reports_list.txt"
                self.pathToDirectory = "/opt/report_generator/done_ftp/"
                self.debug = Debug
                self.dwh = dwh
                self.reportList = self.__openFile()
                self.reportNumber = self.__extractReportInfo()
                self.numberOfActualFiles = 0
                self.numberOfActualDWHFiles = 0
                self.yesterday = (datetime.date.today()) - (datetime.timedelta(days=1))

        #-----------------------------------------------------------------------------------------
        #process textfile

        def __openFile(self):

                try:
                        f = open(self.pathToFile,'r').readlines()
                except IOError:
                        print "file not found"
                        sys.exit(1)
                return f

        def __extractReportInfo(self):#count reports

                reportFile = self.reportList
                reports = {}
                for line in reportFile:
                        line=str(line)
                        line = line.strip()
                        if line.startswith('#'):
                                repoName = line
                                x = 0
                                continue
                        if line:
                                x+=1
                                reports.update({repoName:str(x)})
                if self.debug:
                        print "\nDEBUG: Report List:-"
                        print "===================="
                        for a,b in reports.iteritems():
                                print a + b
                return reports
        #------------------------------------------------------------------------------------------

        #------------------------------------------------------------------------------------------
        #parse directory
        def __getTodaysreports(self):
                altyes = str(self.yesterday)
                altyes = altyes.replace('-','_')
                pattern = "*%s*"%altyes
                now = time.time()
                match = []
                matchDWH = []
                for root, dirnames, filenames in os.walk(self.pathToDirectory):
                        for filename in fnmatch.filter(filenames, '*_%s*'%self.yesterday):
                                match.append(os.path.join(root, filename))
                        for filename in fnmatch.filter(filenames,pattern):
                                matchDWH.append(os.path.join(root, filename))
                if self.debug:
                        print "\nDEBUG: List of todays done files"
                        print "================================"
                        if self.dwh:
                                for x in matchDWH:
                                        if x.endswith('.gpg'):
                                                print x
                        else:
                                for x in match:
                                        if x.endswith('.csv'):
                                                print x

                #Count number of reports in directory
                if self.dwh:
                        for dwhFile in matchDWH:
                                if dwhFile.endswith('.gpg'):
                                        self.numberOfActualDWHFiles+=1
                else:
                        for zipfile in match:
                                if zipfile.endswith('.csv'):
                                        self.numberOfActualFiles+=1

        #------------------------------------------------------------------------------------------	

        def comparereports(self):
                self.__getTodaysreports()
                if self.dwh:
                        try:
                                numberOfExpectedreports = (int(self.reportNumber["#DWH"]))
                        except KeyError:
                                logging.critical("#DWH not found in reports_list.txt")
                                print "CRIT"
                                sys.exit(1)
                        if self.debug:
                                print "\nNumber of expected files:" + str(numberOfExpectedreports)
                                print "Number of actual files:" + str(self.numberOfActualDWHFiles)
                        logging.critical("Number of expected files:%s"%str(numberOfExpectedreports))
                        logging.critical("Number of actual files:%s"%str(self.numberOfActualDWHFiles))
                        if self.numberOfActualDWHFiles == numberOfExpectedreports:
                                print "OK"
                        else:
                                print "CRIT"


                else:
                        numberOfExpectedreports = (int(self.reportNumber["#REPORT1.zip:"]) + int(self.reportNumber["#REPORT2.zip:"]) + int(self.reportNumber["#REPORT3.zip:"])-1)
                        if self.debug:
                                print "\nNumber of expected reports:" + str(numberOfExpectedreports)
                                print "Number of actual reports:" + str(self.numberOfActualFiles)
                        logging.critical("Number of expected reports:%s"%str(numberOfExpectedreports))
                        logging.critical("Number of actual reports:%s"%str(self.numberOfActualFiles))
                        if self.numberOfActualFiles == numberOfExpectedreports:
                                print "OK"
                        else:
                                print "CRIT"

def main():

        logging.basicConfig(format='%(asctime)s %(message)s',filename='repgen.log',level=logging.DEBUG)
        parser = OptionParser()
        parser = OptionParser(conflict_handler="resolve")
        parser.add_option("-v", "--ver", action="store_true", help="Verbose mode")
        parser.add_option("-d", "--dwh", action="store_true", help="DWH ONLY")
        (opts, args) = parser.parse_args()
        a = ReportGenerator(opts.ver,opts.dwh)
        a.comparereports()

if __name__=="__main__":

        main()
