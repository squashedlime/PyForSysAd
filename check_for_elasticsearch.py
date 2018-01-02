#!/usr/bin/env python
import requests, sys
"""
A simple script to extract _status failed inofrmation from elasticsearch 
All outputs are in intergers for zabbix, triggers to be set up for !=0 CRITICAL  9999 CRITICAL no connection 8888 CRITICAL http respose != 200
"""
def collectStatus(url):
    
    try:     
        con = requests.get(url)
	
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
	print "9999"#HTTP CONNECTION ERROR
	sys.exit(0)
	#verify status
    if int(con.status_code) !=200:
	print "8888"#Invalid HTTP response
	sys.exit(0)
    else:
	return con.json()    

def main():
    
    #url = "http://X.X.X.X:9200/_status"
    url = "http://localhost:9200/_status"
    x = collectStatus(url)
    shards = x["_shards"]
    failed = shards["failed"]
    print str(failed)
	
    
if __name__=="__main__":
    
    main()
