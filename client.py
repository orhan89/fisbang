import requests
import json
import random
from datetime import datetime
from time import mktime, sleep

# url  = "http://fisbang-api.appspot.com/"
url  = "http://localhost:8080/"

def get_data():
    v = 220 + int(random.random()*10) - int(random.random()*10)
    i = 5 + random.random()
    p = v*i
    return v, i, p
    
def send_data(sensor, data, time):
    body = json.dumps({"time": time, "value":data})
    print url+"sensor/"+str(sensor)
    try:
        r = requests.post(url+"sensor/"+str(sensor), data=body)
        if r.status_code == 200:
            print "Sending Data {0} at {1} to sensor {2} succeded".format(data,time,sensor)
        else:
            print "Error Sending Data"            
    except:
        print "Error Sending Data"

now = datetime.now()
date = datetime(year = now.year, month=1, day = 1)
time = mktime(date.timetuple())
offset_hour = 60*60
while time < mktime(now.timetuple()):
    data = get_data()
    for idx, sensor_data in enumerate(data):
        send_data(idx, sensor_data, time) 
        # send_data(idx, sensor_data, mktime(datetime.now().timetuple())) # live 
    time += offset_hour
    #sleep(2)
        