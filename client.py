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
    
def send_data(sensor, data):
    time = mktime(datetime.now().timetuple())
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

while True:
    data = get_data()
    for idx, sensor_data in enumerate(data):
        send_data(idx, sensor_data)
    sleep(2)
        