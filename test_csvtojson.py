import csv
import json
import time
import datetime

dataFile = open('data/data-small.csv')
dataReader = csv.DictReader(dataFile, delimiter="\t")

csv_rows = []
json_rows = []
titles = dataReader.fieldnames

for row in dataReader:
    #print row
    csv_rows.extend([{titles[i]:row[titles[i]] for i in range(len(titles))}])

for row in csv_rows:
    mdate = row["Date"] + "T" + row["Time"] + ":00Z"
    dt = time.strptime(mdate, "%Y-%b-%dT%H:%M:00Z")
    _time = str(int(time.mktime(dt)))+"000000"
    #print _time
    row["time"] = _time
    print row
    json_row = {
        "measurement": "broadbandspeed",
        "time": _time,
        "tags": {
            "isp_ip_address": row["ISP_IP_Address"],
            "isp": row["ISP"],
            "date": row["Date"],
            "dtime": row["Time"],
            "target_server": row["TargetSever"]
        },
        "values": {
            "upload_mbs": row["Upload_Mbs"],
            "download_mbs": row["Download_Mbs"],
            "ping_ms": row["Ping_ms"],
            "distance_km": row["Distance_km"]
        }
    }

    print(json.dumps(json_row))
    json_rows.append(json_row)

#print(json.dumps(csv_rows, sort_keys=False, indent=4, separators=(',', ': '), encoding="UTF-8", ensure_ascii=False))
print(json.dumps(json_rows, sort_keys=False, indent=4))
dataFile.close()

