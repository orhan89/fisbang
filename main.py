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

class SensorData(ndb.Model):
    sensor_id = ndb.IntegerProperty(indexed=True)
    value = ndb.IntegerProperty(indexed=False)
    time = ndb.DateTimeProperty(auto_now_add=True)

class SensorHandler(webapp2.RequestHandler):

    def get(self, sensor_id):

        if not isinstance(sensor_id, int):
            sensor_id = int(sensor_id)

        query = SensorData.query(SensorData.sensor_id == sensor_id).order(-SensorData.time)
        sensors_data = query.fetch()

        response_data = []
        for sensor_data in sensors_data:
            timestamp = mktime(sensor_data.time.timetuple())
            response_data.append({'value': sensor_data.value, 'time': timestamp})
        self.response.headers['Access-Control-Allow-Origin'] = 'http://www.fisbang.com'
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response_data))
        

    def post(self, sensor_id):

        request_data = json.loads(self.request.body)
        if not isinstance(sensor_id, int):
            sensor_id = int(sensor_id)
        if 'value' in request_data:
            value = request_data['value']
        if 'time' in request_data:
            time = datetime.fromtimestamp(request_data['time'])

        sensor_data = SensorData()
        sensor_data.sensor_id = sensor_id
        sensor_data.value = value
        if time:
            sensor_data.time = time

        obj = sensor_data.put()
        self.response.write(str(obj.id()))

app = webapp2.WSGIApplication([
    ('/sensor/(\d+)', SensorHandler)
], debug=True)
