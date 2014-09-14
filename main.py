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

SENSOR_TYPE = ((0, "voltage"),
               (1, "current"))

def get_sensor_data(sensor_id, time=None, limit=None):
    sensor_data = memcache.get('sensor_data:%s' % sensor_id)
    if sensor_data is None:
        sensor = ndb.Key(urlsafe=sensor_id).get()

        if sensor:
            sensor_data = json.loads(sensor.data)
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

class Sensor(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    type = ndb.IntegerProperty()
    data = ndb.StringProperty(indexed=False)
    
    @classmethod
    def query_sensor(cls, sensor_id):
        return cls.query(Sensor.id==sensor_id)

class Device(ndb.Model):
    name = ndb.StringProperty(indexed=False)

class Environment(ndb.Model):
    name = ndb.StringProperty(indexed=False)

class Building(ndb.Model):
    name = ndb.StringProperty(indexed=False)

class TotalEnergyHandler(webapp2.RequestHandler):

    def get(self, sensor_id):

        now = datetime.now()
        days_number = now.isocalendar()[1]*7 + now.isocalendar()[2]
        energy_data = memcache.get('energy_data:%s' %(sensor_id))

        if energy_data is None:
            all_sensor_data = get_sensor_data(sensor_id)

            start_date = datetime(year = now.year, month=1, day = 1)
            offset_day = timedelta(days=1)

            energy_data= [ {'value':(lambda xs: (sum(xs)/len(xs)if xs else 0)*((now-start_date).days*24))([data['value'] for data in all_sensor_data if data['time'] > float(mktime(start_date.timetuple())) and data['time'] < float(mktime(now.timetuple()))]), 'start_time':float(mktime(start_date.timetuple())), 'end_time':float(mktime(now.timetuple()))} ]

            memcache.add('energy_data:%s' % (sensor_id), energy_data, 60)

        if not energy_data is None:
            #self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.com'
            self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.local'
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(energy_data))
        else:
            self.response.status = 404
            self.response.write("Sensor not found")

class TotalEnergy2Handler(webapp2.RequestHandler):

    def get(self, sensor_id, wattage):

        now = datetime.now()
        days_number = now.isocalendar()[1]*7 + now.isocalendar()[2]
        ratio = float(wattage)/20
        print ratio
        energy_data = memcache.get('energy2_data:%s:%s' %(sensor_id, ratio))

        if energy_data is None:
            all_sensor_data = get_sensor_data(sensor_id)

            start_date = datetime(year = now.year, month=1, day = 1)
            offset_day = timedelta(days=1)

            energy_data= [ {'value':(lambda xs: (sum(xs)/len(xs)if xs else 0)*((now-start_date).days*24))([data['value']*ratio for data in all_sensor_data if data['time'] > float(mktime(start_date.timetuple())) and data['time'] < float(mktime(now.timetuple()))]), 'start_time':float(mktime(start_date.timetuple())), 'end_time':float(mktime(now.timetuple()))} ]

            memcache.add('energy2_data:%s:%s' % (sensor_id, ratio), energy_data, 60)

        if not energy_data is None:
            #self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.com'
            self.response.headers['Access-Control-Allow-Origin'] = 'http://app.fisbang.local'
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(energy_data))
        else:
            self.response.status = 404
            self.response.write("Sensor not found")

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

        sensor = ndb.Key(urlsafe=sensor_id).get()
        if not sensor:
            self.response.write("Sensor Not Found")

        data = json.loads(sensor[0].data)

        data.append(json.loads(self.request.body))
        sensor[0].data = json.dumps(data)
        sensor[0].put()
        if memcache.get('sensor_data:%s' % sensor_id):
            print "Updating memcache"
            memcache.set("sensor_data:%s" % sensor_id, data)
        else:
            print "Create new memcache"
            memcache.add('sensor_data:%s' % sensor_id, data, 60)        
        self.response.write("OK")


class SensorHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        device_id = request_data['device_id']
        name = request_data['name']
        sensor_type = request_data['type']

        sensor_list = Sensor.query(ancestor=ndb.Key(urlsafe=device_id)).fetch()
        
        print "Create new sensor"
        sensor = Sensor(parent=ndb.Key(urlsafe=device_id))
        
        sensor.name = name
        sensor.data = json.dumps([])
        sensor.type = sensor_type
        key = sensor.put()
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({"sensor_id": key.urlsafe()}))

class DeviceHandler(webapp2.RequestHandler):
    def get(self, device_id):
        sensor_list = Sensor.query(ancestor=ndb.Key(urlsafe=device_id)).fetch()

        sensor_id_list = [{"id":item.key.urlsafe(), "type":item.type} for item in sensor_list]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({"sensors":sensor_id_list}))

    def post(self):
        request_data = json.loads(self.request.body)
        environment_id = request_data['environment_id']
        name = request_data['name']

        print "Create new device"
        device = Device(parent=ndb.Key(urlsafe=environment_id))
        
        device.name = name
        key = device.put()
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({"device_id": key.urlsafe()}))


class EnvironmentHandler(webapp2.RequestHandler):
    def get(self, environment_id):
        device_list = Device.query(ancestor=ndb.Key('Environment', environment_id)).fetch()

        device_id_list = [{"id":item.key.urlsafe(), "name":item.name} for item in device_list]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({"devices":device_id_list}))

    def post(self):
        request_data = json.loads(self.request.body)
        building_id = request_data['building_id']
        name = request_data['name']

        print "Create new environment"
        environment = Environment(parent=ndb.Key(urlsafe=building_id))
        
        environment.name = name
        key = environment.put()
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({"environment_id": key.urlsafe()}))

class BuildingHandler(webapp2.RequestHandler):
    def get(self, building_id):
        environment_list = Environment.query(ancestor=ndb.Key('Building', building_id)).fetch()

        environment_id_list = [{"id":item.key.urlsafe(), "name":item.name} for item in environment_list]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({"environments":environment_id_list}))

    def post(self):
        request_data = json.loads(self.request.body)
        name = request_data['name']

        print "Create new building"
        building = Building()
        
        building.name = name
        key = building.put()
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({"building_id": key.urlsafe()}))

# app = webapp2.WSGIApplication([
#     ('/sensor/(\s)', SensorDataHandler),
#     ('/sensor/(\d+)/monthly', MonthlyHandler),
#     ('/sensor/(\d+)/weekly', WeeklyHandler),
#     ('/sensor/(\d+)/daily', DailyHandler),
#     ('/sensor/(\d+)/energy', TotalEnergyHandler),
#     ('/sensor/(\d+)/energy2/(\d+)', TotalEnergy2Handler),
#     ('/sensor', SensorHandler),
#     ('/device/(\d+)', DeviceHandler)
# ], debug=True)

app = webapp2.WSGIApplication([
    webapp2.Route(r'/building', handler=BuildingHandler, methods=['POST']),
    webapp2.Route(r'/building/<building_id>', handler=BuildingHandler, methods=['GET']),
    webapp2.Route(r'/environment', handler=EnvironmentHandler, methods=['POST']),
    webapp2.Route(r'/environment/<environment_id>', handler=EnvironmentHandler, methods=['GET']),
    webapp2.Route(r'/device', handler=DeviceHandler, methods=['POST']),
    webapp2.Route(r'/device/<device_id>', handler=DeviceHandler, methods=['GET']),
    webapp2.Route(r'/sensor', handler=SensorHandler),
    webapp2.Route(r'/sensor/<sensor_id>', handler=SensorDataHandler),
    webapp2.Route(r'/sensor/<sensor_id>/daily', handler=DailyHandler),
    webapp2.Route(r'/sensor/<sensor_id>/weekly', handler=WeeklyHandler),
    webapp2.Route(r'/sensor/<sensor_id>/monthly', handler=MonthlyHandler),
    webapp2.Route(r'/sensor/<sensor_id>/energy', handler=TotalEnergy2Handler),
    webapp2.Route(r'/sensor/<sensor_id>/energy2/<wattage>', handler=TotalEnergy2Handler),
], debug=True)
