#!/usr/bin/env python
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
import subprocess
import re
import datetime
import csv

## Global variables
# Directory where this script is located
BROADBAND_SPEED_HOME="e:/work/broadbandspeed"
# The path and name of the data file.
DATAFILE = BROADBAND_SPEED_HOME + "/data/data.csv"
# The location of the speedtest package that was installed via pip
SPEEDTEST="e:\python\python27\Scripts\speedtest.exe"
# Set TEST=True for testing
TEST=False
# Start time
#NOW = datetime.datetime.now().strftime("%Y-%b-%d %H:%M")
NOWDATE = datetime.datetime.now().strftime("%Y-%b-%d")
NOWTIME = datetime.datetime.now().strftime("%H:%M")

# Test the TEST condition
if( TEST == False):
    """If TEST is false, then run the speedtest-cli module to
        obtain actual numbers for the ISP """
    result = str(subprocess.check_output(SPEEDTEST))
else:
    """If TEST is true, then use this canned data"""
    result = """Retrieving speedtest.net configuration...
Retrieving speedtest.net server list...
Testing from PlusNet Technologies Ltd (212.159.103.14)...
Selecting best server based on latency...
Hosted by Fasthosts Internet (Gloucester) [29.59 km]: 19.812 ms
Testing download speed........................................
Download: 31.44 Mbit/s
Testing upload speed..................................................
Upload: 6.00 Mbit/s"""


"""Get ISP and IP Address"""
pattern = re.compile("^Testing from (.*) \((.*)\)", re.MULTILINE)
matches = pattern.search(result)
ISP = matches.group(1)
IPADDR = matches.group(2)

"""Get Host, distance and Ping"""
pattern = re.compile("^Hosted by (.*).\[(\d*.\d*).*\]: (\d*.\d*)", re.MULTILINE)
matches = pattern.search(result)
HOST = matches.group(1)
DISTANCE = matches.group(2)
PING = matches.group(3)

"""Get Download speed"""
pattern = re.compile("^Download:\s+(\d+.\d+)", re.MULTILINE)
matches = pattern.search(result)
DOWNLOAD = matches.group(1)

"""Get Upload speed"""
pattern = re.compile("^Upload: (\d+.\d+)", re.MULTILINE)
matches = pattern.search(result)
UPLOAD = matches.group(1)

if (TEST == True):
    """Print the results to STDOUT """
    print "Date:{} Time:{} ISP:{} IPADRR:{} HOST:{} DISTANCE:{} PING:{} DOWNLOAD:{} UPLOAD:{}".format(NOWDATE, NOWTIME, ISP, IPADDR, HOST, DISTANCE, PING, DOWNLOAD, UPLOAD)

""" Write the results to a data file """   
with open(DATAFILE, "ab") as csv_file:
    writer = csv.writer(csv_file, dialect = "excel-tab", quotechar='"')
    writer.writerow([NOWDATE, NOWTIME, ISP, IPADDR, HOST, DISTANCE, PING, DOWNLOAD, UPLOAD])

# Finish