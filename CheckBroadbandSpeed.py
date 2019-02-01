#!/usr/bin/env python 
import subprocess
import re
import datetime
import csv
from ConfigParser import SafeConfigParser
import os
import sys
import json
import time
from influxdb import InfluxDBClient

"""
@Name:      CheckBroadbandSpeed.py
@Author:    Richard Lucas
@Date:      7-Feb-2016
@Purpose:   Implementation of Alasdair Allan's 'Use Raspberry Pi to Measure
            Broadband Speeds to hold your ISP Accountable'
            http://makezine.com/projects/send-ticket-isp-when-your-internet-drops/
            This script is takes the output of the 'speedtest-cli' module
            and transforms the output into a single line of data to be appended
            to a tab-delimited file.
            Future iterations may change for charting with a library such as
            HighCharts, or for implementing an RRDTool type tool.
            
            Also the script will introduce error handling, and using functions.
"""
# -----------------------------------------------------------------------------
# Global variables
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

class CannedData(object):
    '''This class stores some test data for testing changes to the code
    without the need to peform a real test'''
    
    cannedData = """Retrieving speedtest.net configuration...
Retrieving speedtest.net server list...
Testing from PlusNet Technologies Ltd (67.198.33.99)...
Selecting best server based on latency...
Hosted by Fasthosts Internet (Gloucester) [29.59 km]: 19.812 ms
Testing download speed........................................
Download: 31.44 Mbit/s
Testing upload speed..................................................
Upload: 6.00 Mbit/s"""

    @classmethod
    def getCannedData(cls):
        return cls.cannedData

# -----------------------------------------------------------------------------

class CheckBroadbandSpeed:
  
    # Directory where this script is located - configured in config.ini
    BROADBAND_SPEED_HOME = None
    # The path and name of the data file - configured in config.ini
    DATAFILE_HOME = None
    # The location of the speedtest package that was installed via pip  - configured in config.ini
    SPEEDTEST_HOME = None
    # Set test=True for testing; Test=False for real measurements in config.ini
    TEST=False
    # Start time
    NOWDATE = datetime.datetime.now().strftime("%Y-%b-%d")
    NOWTIME = datetime.datetime.now().strftime("%H:%M")
    
    # -----------------------------------------------------------------------------
    def getSpeedtestResult(TEST, SPEEDTEST_HOME):
        '''
        Returns the result of the speedtest.
        If the test mode is enabled in the config.ini (test=True)then it will return
        the canned data
        '''
        if( TEST == False):
            """If TEST is false, then run the speedtest-cli module to
                obtain actual numbers for the ISP """
            
            return str(subprocess.check_output(SPEEDTEST_HOME))
        else:
            """If TEST is true, then use this canned data"""
            return CannedData.getCannedData()
    
    # -----------------------------------------------------------------------------
    
    def getMatches(result, rxPattern, rxGroups):
    # result is the speedtest result string
    # rxPattern is the regular expression to use
    # rxGroups is the List of match groups to return
    # example:
    # ISP, IPADDR = getMatches(speedTestResult, "^Testing from (.*) \((.*)\)", (1,2))

        pattern = re.compile(rxPattern, re.MULTILINE)
        matches = pattern.search(result)
        return matches.groups(rxGroups)

    # -----------------------------------------------------------------------------
    def updateInfluxDb(client, row):
        mdate = row["Date"] + "T" + row["Time"] + ":00Z"
        dt = time.strptime(mdate, "%Y-%b-%dT%H:%M:00Z")
        _time = str(int(time.mktime(dt)))
        # print _time
        row["time"] = _time
        # print row
        json_row = [
            {
                "measurement": "broadbandspeed",
                "time": mdate,
                "tags": {
                    "isp_ip_address": row["ISP_IP_Address"],
                    "isp": row["ISP"],
                    "date": row["Date"],
                    "dtime": row["Time"],
                    "target_server": row["TargetSever"]
                },
                "fields": {
                    "upload_mbs": float(row["Upload_Mbs"]),
                    "download_mbs": float(row["Download_Mbs"]),
                    "ping_ms": float(row["Ping_ms"]),
                    "distance_km": float(row["Distance_km"])
                }
            }
        ]
        print(json.dumps(json_row))
        client.write_points(json_row)


    # ==============================================================================
    
    if __name__ == '__main__':
    
        BROADBAND_SPEED_HOME = os.path.dirname(__file__)
        try:
            parser = SafeConfigParser()
            parser.read(os.path.join(os.path.dirname(__file__),"config.ini"))
        except:
            print("Error: Could not read file 'config.ini'. Please check it exists in the same directory as CheckBroadbandSpeed.py")
            sys.exit(1)
       
        # The path and name of the data file - configured in config.ini
        DATAFILE_HOME =  parser.get('location','datafile')
        if ( not os.path.exists(DATAFILE_HOME)):
            print("Error: Could not locate the data file in {}" ).format(DATAFILE_HOME)
            sys.exit(1)
            
        # The location of the speedtest package that was installed via pip  - configured in config.ini
        SPEEDTEST_HOME = parser.get('location','speedtest')
        if ( not os.path.exists(SPEEDTEST_HOME)):
            print("Error: Could not locate the speedtest library in {}" ).format(SPEEDTEST_HOME)
            sys.exit(1)

        # Configure the Influx database client connection
        host = parser.get('database', 'host')
        port = parser.get('database', 'port')
        db = parser.get('database', 'db')
        # Connect to the database
        client = InfluxDBClient(host, port, '', '', db)

        # Set test=True for testing; Test=False for real measurements in config.ini
        TEST=parser.getboolean('mode','test')
        # Start time
        NOWDATE = datetime.datetime.now().strftime("%Y-%b-%d")
        NOWTIME = datetime.datetime.now().strftime("%H:%M")    


        """Run the Speedtest"""
        speedTestResult = getSpeedtestResult(TEST, SPEEDTEST_HOME)
            
        """Get ISP and IP Address"""
        ISP, IPADDR = getMatches(speedTestResult, "^Testing from (.*) \((.*)\)", (1,2))
        
        """Get Host, distance and Ping"""
        HOST, DISTANCE, PING = getMatches(speedTestResult, "^Hosted by (.*).\[(\d*.\d*).*\]: (\d*.\d*)", (1,2,3))
        
        """Get Download speed"""
        DOWNLOAD = getMatches(speedTestResult, "^Download:\s+(\d+.\d+)", (1))[0]
        
        """Get Upload speed"""
        UPLOAD = getMatches(speedTestResult, "^Upload: (\d+.\d+)", (1))[0]
        
        if (TEST == True):
            """Print the results to STDOUT """
            result = "Date:{} Time:{} ISP:{} IPADRR:{} HOST:{} DISTANCE:{} PING:{} DOWNLOAD:{} UPLOAD:{}".format(NOWDATE, NOWTIME, ISP, IPADDR, HOST, DISTANCE, PING, DOWNLOAD, UPLOAD)
            print result
            assert result == "Date:{} Time:{} ISP:PlusNet Technologies Ltd IPADRR:67.198.33.99 HOST:Fasthosts Internet (Gloucester) DISTANCE:29.59 PING:19.812 DOWNLOAD:31.44 UPLOAD:6.00".format(NOWDATE, NOWTIME)
            assert ISP == "PlusNet Technologies Ltd", "ISP should be PlusNet Technologies but got %s" % ISP
            assert IPADDR == "67.198.33.99", "IP should be 67.198.33.99 but got %s" % IP
            assert HOST == "Fasthosts Internet (Gloucester)", "HOST should be Fasthosts Internet (Glocester) but got %s" % HOST
            assert DISTANCE == "29.59", "DISTANCE should be 29.59 but got %s" % DISTANCE
            assert PING == "19.812", "PING should be 19.812 but got %s" % PING
            assert DOWNLOAD == "31.44", "DOWNLOAD should be 31.44 but got %s" % DOWNLOAD
            assert UPLOAD == "6.00", "UPLOAD should be 6.00 but got %s" % UPLOAD
            
        
        """ Write the results to a data file """   
        with open(DATAFILE_HOME, "ab") as csv_file:
            writer = csv.writer(csv_file, dialect = "excel-tab", quotechar='"')
            writer.writerow([NOWDATE, NOWTIME, ISP, IPADDR, HOST, DISTANCE, PING, DOWNLOAD, UPLOAD])

        """ Write the results to the Influx DB"""

        updateInfluxDb(client, {"Date": NOWDATE,
                                "Time": NOWTIME,
                                "ISP": ISP,
                                "ISP_IP_Address": IPADDR,
                                "TargetServer": HOST,
                                "Upload_Mbs": UPLOAD,
                                "Download_Mbs": DOWNLOAD,
                                "Ping_Ms": PING,
                                "Distance_km": DISTANCE
                            }
                       )

# Finish