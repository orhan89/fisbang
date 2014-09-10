#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
from datetime import datetime, timedelta
from time import mktime

from google.appengine.ext import ndb
from google.appengine.api import memcache

STANDARD_LIMIT = 100

def get_sensor_data(sensor_id, time=None, limit=None):
    sensor_data = memcache.get('sensor_data:%s' % sensor_id)
    if sensor_data is None:
        sensor_data = SensorData.query_sensor(sensor_id).fetch(1)

        if sensor_data:
            sensor_data = json.loads(sensor_data[0].data)
            memcache.add('sensor_data:%s' % sensor_id, sensor_data, 60)
        else:
            return None
    else:
        print "Using data from Memcache"
        print memcache.get_stats()

    if time:
        sensor_data = [data for data in sensor_data if data['time'] > float(time)]

    if isinstance(limit, int) and len(sensor_data) > int(limit):
        sensor_data = sensor_data[-int(limit):]

    return sensor_data

class SensorData(ndb.Model):
    data = ndb.StringProperty(indexed=False)

    @classmethod
    def query_sensor(cls, sensor_id):
        return cls.query(ancestor=ndb.Key('Sensor', sensor_id))


class DailyHandler(webapp2.RequestHandler):

    def get(self, sensor_id):

        now = datetime.now()
        days_number = now.isocalendar()[1]*7 + now.isocalendar()[2]
        sensor_data = memcache.get('sensor_data:%s:daily:%s' %(sensor_id, days_number))
                                   
        if sensor_data is None:
        
            all_sensor_data = get_sensor_data(sensor_id)
    
            date = datetime(year = now.year, month=1, day = 1)
            offset_day = timedelta(days=1)
    
            sensor_data= [{'value':(lambda xs: sum(xs)/len(xs) if xs else 0)([data['value'] for data in all_sensor_data if data['time'] > float(mktime((date+days*offset_day).timetuple())) and data['time'] < float(mktime((date+(days+1)*offset_day).timetuple()))]), 'days':(days+1), 'time':float(mktime((date+days*offset_day).timetuple()))} for days in range(0,(now.isocalendar()[1]*7+now.isocalendar()[2]))]

            memcache.add('sensor_data:%s:daily:%s' % (sensor_id, days_number), sensor_data, 60)

        if not sensor_data is None:
            #self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.com'
            self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.local'
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(sensor_data))
        else:
            self.response.status = 404
            self.response.write("Sensor not found")

class WeeklyHandler(webapp2.RequestHandler):

    def get(self, sensor_id):

        now = datetime.now()
        weeks_number = now.isocalendar()[1]
        sensor_data = memcache.get('sensor_data:%s:weekly:%s' %(sensor_id, weeks_number))

        if sensor_data is None:
            all_sensor_data = get_sensor_data(sensor_id)
    
            date = datetime(year = now.year, month=1, day = 1)
            offset_week = timedelta(weeks=1)
    
            sensor_data= [{'value':(lambda xs: sum(xs)/len(xs) if xs else 0)([data['value'] for data in all_sensor_data if data['time'] > float(mktime((date+week*offset_week).timetuple())) and data['time'] < float(mktime((date+(week+1)*offset_week).timetuple()))]), 'week':(week+1),  'time':float(mktime((date+week*offset_week).timetuple()))} for week in range(0,now.isocalendar()[1])]
                                   
            memcache.add('sensor_data:%s:weekly:%s' % (sensor_id, weeks_number), sensor_data, 60)

        if not sensor_data is None:
            #self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.com'
            self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.local'
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(sensor_data))
        else:
            self.response.status = 404
            self.response.write("Sensor not found")

class MonthlyHandler(webapp2.RequestHandler):

    def get(self, sensor_id):


        now = datetime.now()
        months_number = now.month
        sensor_data = memcache.get('sensor_data:%s:monthly:%s' %(sensor_id, months_number))

        if sensor_data is None:
            all_sensor_data = get_sensor_data(sensor_id)
    
            date = datetime(year = now.year, month=1, day = 1)
    
            sensor_data= [{'value':(lambda xs: sum(xs)/len(xs) if xs else 0)([data['value'] for data in all_sensor_data if data['time'] >= float(mktime((datetime(year=now.year, month=(months+1), day=1)).timetuple())) and data['time'] < float(mktime((datetime(year=now.year, month=(months+2), day=1)).timetuple()))]), 'month':(months+1),  'time':float(mktime((datetime(year=now.year, month=(months+1), day=1)).timetuple()))} for months in range(0,(now.month))]

            memcache.add('sensor_data:%s:monthly:%s' % (sensor_id, months_number), sensor_data, 60)

        if not sensor_data is None:
            #self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.com'
            self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.local'
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(sensor_data))
        else:
            self.response.status = 404
            self.response.write("Sensor not found")

class SensorDataHandler(webapp2.RequestHandler):

    def get(self, sensor_id):

        time = self.request.get('time', None)
        limit= self.request.get('limit', STANDARD_LIMIT)

        sensor_data = get_sensor_data(sensor_id, time,limit)

        if not sensor_data is None:
            #self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.com'
            self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.local'
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(sensor_data))
        else:
            self.response.status = 404
            self.response.write("Sensor not found")

    def post(self, sensor_id):

        sensor_data = SensorData.query_sensor(sensor_id).fetch(1)
        if not sensor_data:
            print "Create new sensor data"
            sensor_data = SensorData(parent=ndb.Key('Sensor', sensor_id))
            data = []
        else:
            print "Using existing sensor data"
            sensor_data = sensor_data[0]
            data = json.loads(sensor_data.data)

        data.append(json.loads(self.request.body))
        sensor_data.data = json.dumps(data)
        sensor_data.put()
        if memcache.get('sensor_data:%s' % sensor_id):
            print "Updating memcache"
            memcache.set("sensor_data:%s" % sensor_id, data)
        else:
            print "Create new memcache"
            memcache.add('sensor_data:%s' % sensor_id, data, 60)        
        self.response.write("OK")

app = webapp2.WSGIApplication([
    ('/sensor/(\d+)', SensorDataHandler),
    ('/sensor/(\d+)/monthly', MonthlyHandler),
    ('/sensor/(\d+)/weekly', WeeklyHandler),
    ('/sensor/(\d+)/daily', DailyHandler)
], debug=True)
