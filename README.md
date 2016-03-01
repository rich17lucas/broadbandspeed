# broadbandspeed
Implementation of Alasdair Allan's 'Use Raspberry Pi to Measure Broadband Speeds to hold your ISP Accountable'             http://makezine.com/projects/send-ticket-isp-when-your-internet-drops/             This script is takes the output of the 'speedtest-cli' module             and transforms the output into a single line of data to be appended             to a tab-delimited file.             Future iterations may change for charting with a library such as HighCharts, or for implementing an RRDTool type tool.

## Installation
1. Install Python 2.7.11+ _which includes PIP_
2. Use PIP to install speedtest_cli
3. `pip install speedtest_cli`
4. Checkout CheckBroadbandSpeed.py to a location
5. Edit the location variables in the top of the script and save it.
6. Setup a Scheduled Task (Windows) or a cron job ('Nix OS)


## ToDo
Use ConfigParser to read configuration file for locations of Python, speedtestcli, and broadbandspeed directories
