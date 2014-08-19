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
from datetime import datetime
from time import mktime

from google.appengine.ext import ndb

STANDARD_LIMIT = 100

class SensorData(ndb.Model):
    data = ndb.StringProperty(indexed=False)

    @classmethod
    def query_sensor(cls, sensor_id):
        return cls.query(ancestor=ndb.Key('Sensor', sensor_id))


class SensorHandler(webapp2.RequestHandler):

    def get(self, sensor_id):

        sensor_data = SensorData.query_sensor(sensor_id).fetch(1)

        if sensor_data:
            sensor_data = json.loads(sensor_data[0].data)

            time = self.request.get('time')
            if time:
                sensor_data = [data for data in sensor_data if data['time'] >= float(time)]

            limit= self.request.get('limit', STANDARD_LIMIT)
            print limit
            if len(sensor_data) > int(limit):
                sensor_data = sensor_data[-int(limit):]

            self.response.headers['Access-Control-Allow-Origin'] = 'http://www.fisbang.com'
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
        self.response.write("OK")

app = webapp2.WSGIApplication([
    ('/sensor/(\d+)', SensorHandler)
], debug=True)
