#!/usr/bin/python

import json
import urllib2

# Get JSON data from sfgov.org for foodtrucks and locations
try:
    response = urllib2.urlopen('http://data.sfgov.org/resource/rqzj-sfat.json?status=APPROVED')
    data = json.load(response)
except:
    exit('ERROR: Failed loading JSON Source')

# Collections for each model in db
trucks = []
locations = []
schedules = []

for entry in data:

    # Truck Info
    if 'permit' in entry:
        permit = entry['permit']
    else:
        continue
    fooditems = ''
    applicant = ''
    if 'fooditems' in entry:
        fooditems = entry['fooditems']
    if 'applicant' in entry:
        applicant = entry['applicant']
    # We only want unique trucks
    if not any(truck['pk'] == permit for truck in trucks):
        trucks.append(dict(pk=permit, model='foodtrucks.truck', fields=dict(fooditems=fooditems, applicant=applicant)))

    # Location Info
    if 'objectid' in entry:
        locationid = entry['objectid']
    else:
        continue
    address = ''
    loc_desc = ''
    lat = 0.0
    lng = 0.0
    if 'address' in entry:
        address = entry['address']
    if 'locationdescription' in entry:
        loc_desc = entry['locationdescription']
    if 'latitude' in entry:
        lat = entry['latitude']
    if 'longitude' in entry:
        lng = entry['longitude']
    # Unique Locations. Actually always true..
    if not any(location['pk'] == locationid for location in locations):
        locations.append(dict(pk=locationid, model='foodtrucks.location',
                              fields=dict(address=address, truck=permit, description=loc_desc, lat=float(lat),long=float(lng))))

    # Schedule data for location. Schedule data is in a different API
    try:
        req_url = 'http://data.sfgov.org/resource/jjew-r69b.json?locationid='+locationid
        response = urllib2.urlopen(req_url)
        schedule_data = json.load(response)
    except:
        continue
    for schedule in schedule_data:
        if 'scheduleid' in schedule and 'dayorder' in schedule:
            sid = schedule['scheduleid']
            day_of_week = schedule['dayorder']  # Sun-Sat ---  0-6
        else:
            continue
        start_time = '00:00'
        end_time = '23:59'
        if 'start24' in schedule:
            start_time = schedule['start24']
        if 'end24' in schedule:
            end_time = schedule['end24']
        # Only unique schedule will be added. Lots of duplicates in sfgov data
        if not any(schedule['fields']['location'] == locationid and schedule['fields']['dayofweek'] == day_of_week and schedule['fields']['starttime'] == start_time and schedule['fields']['endtime'] == end_time for schedule in schedules):
            schedules.append(dict(pk=sid, model='foodtrucks.schedule',
                                  fields=dict(location=locationid, truck=permit, dayofweek=day_of_week, starttime=start_time, endtime=end_time)))
    # Keep track of progress.
    print "Percentage Done: %.2f%%\r" % (float(len(locations))/len(data) * 100),

# Merge all three collections to create one fixture
items = trucks + locations + schedules
try:
    f = open('data.json', 'w')
    f.write(json.dumps(items))
    f.close()
except:
    print "\nERROR: Failed to create json file"

print "Percentage Done: 100.00%\nFixture creation COMPLETE!"
