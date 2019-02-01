#import urllib
#import urllib2
from influxdb import InfluxDBClient
import json

#contents = urllib2.urlopen("http://bbc.co.uk").read()
#urllib2.urlopen("http://bluebot:8086/query?pretty=true --data-urlencode \"db=mydb\" --data-urlencode \"q=SELECT \"value\" FROM \"cpu_load_short\" WHERE \"region\"='us-west'\"")
#contents = urllib2.urlopen('http://bluebot:8086/query?pretty=true&db=mydb&q=select * from "cpu"').read()

#data = {}
#data['pretty'] = 'true'
#data['db'] = 'mydb'
#data['q'] = 'select "*" from "cpu"'

#print data


client = InfluxDBClient("bluebot","8086",'' ,'','mydb')
print client.get_list_database()
result = client.query("select * from broadbandspeed;")
print json.dumps(result, indent=4)


