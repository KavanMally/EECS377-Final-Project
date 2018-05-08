#!/usr/bin/python
import unirest 
import json 
from collections import defaultdict
from datetime import datetime, timedelta, date
from pytz import timezone

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, timedelta):
        return str(obj)

    raise TypeError ("Type %s not serializable" % type(obj))

def dt_parse(t, s):
    ret = datetime.strptime(t[0:16], s)
    if t[18]=='+':
        ret-=timedelta(hours=int(t[19:22]),minutes=int(t[23:]))
    elif t[18]=='-':
        ret+=timedelta(hours=int(t[19:22]),minutes=int(t[23:]))
    return ret

def __datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S-04:00')

times = unirest.get("https://transloc-api-1-2.p.mashape.com/arrival-estimates.json?agencies=1199", headers={"X-Mashape-Key": "LJJSa7y5V6mshHSJB4rKmlbBon5cp1tUfZ7jsn0iEqV4YsNNvK","Accept": "application/json"})

stops = unirest.get("https://transloc-api-1-2.p.mashape.com/stops.json?agencies=1199",
  headers={
    "X-Mashape-Key": "LJJSa7y5V6mshHSJB4rKmlbBon5cp1tUfZ7jsn0iEqV4YsNNvK",
    "Accept": "application/json"
  }
)


#print json.dumps(times.body['data'], indent=2, sort_keys=True)
#print json.dumps(stops.body['data'], indent=2, sort_keys=True)

"""
Since the json just gives us stop ID's, lets generate a dict of stop id's and human readable names as a lookup table

"""
stops_list = {}
stops = stops.body['data']

for i in xrange(len(stops)):
    stops_list[stops[i]['stop_id']] = stops[i]['name']

#print json.dumps(stops_list, indent=2)


"""
The way the times are organized, the stop id is in the outer level, while the arrival time is in an inner level.

Steps:

0. Create an empty list to append from these mismatched levels
1. iterate and append the stop_id, step in a level and append the arrival time
2. Since each arrival creates a new entry the defaultdict is used to combine all arrivals pertaining to a single stop
3. json.dumps() is used to neatly indent it

"""
final = []
time = times.body['data']
for i in xrange(len(time)):
    for j in xrange(len(time[i]['arrivals'])):
        final.append({time[i]['stop_id'] : time[i]['arrivals'][j]['arrival_at']})

dd = defaultdict(list)
t = timezone('America/New_York').localize(datetime.now()).replace(microsecond=0).isoformat()

for d in final:
     for key, value in d.iteritems():
        s = (__datetime(value) - __datetime(t)).total_seconds()
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            dd[stops_list[key]].append('Arriving In: %s Hours and %s minutes' % (int(hours),int(minutes)))
        else:
            dd[stops_list[key]].append('Arriving In: %s minutes and %s seconds' % (int(minutes),int(seconds)))

#print json.dumps(dict(dd), indent=2, default=json_serial)

print(dd["Village Stop A"][0])
