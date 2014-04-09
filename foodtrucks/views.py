from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q  # for advanced query construction
from foodtrucks.models import Truck, Location

import operator
import json
import re

# foodtruck/ routes here
# simply return the index.html template page
def index(request):
    return render(request, 'foodtrucks/index.html')

# call to handle ajax request
# return the truck info according to the filter
def get_trucks(request):
    locations = Location.objects.all()
    if('foodItems' in request.GET) :
        # split the foodItems string to arraylist
        items = re.split('[\s,;.]+', request.GET['foodItems'])
        # for each item check whether in fooditem field or truck name, 'OR' them together
        if(len(items) > 0 and items[0] != ''): 
            Qs = []
            for item in items:
                Qs.append(Q(truck__fooditems__icontains=item))
                Qs.append(Q(truck__applicant__icontains=item))
            locations = locations.filter(reduce(operator.__or__,Qs))

    if('openOnly' in request.GET and request.GET['openOnly'] == 'true') :
        locations = [location for location in locations if location.isOpenNow()] # List Comprehension to get only opening location
    result_set = []
    for location in locations:
        result = dict(lat=location.lat, lng=location.long, name=location.truck.applicant, address=location.address, schedule=location.getTodaySchedule(), opennow=location.isOpenNow())
        result_set.append(result)
    # return the constructed data blob in JSON format
    return HttpResponse(json.dumps(result_set), content_type="application/json");
