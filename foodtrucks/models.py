from django.db import models
from datetime import datetime, time

# Truck Model
# PK:     permitid
# Fields: 
#         applicant
#         fooditems
class Truck(models.Model):
    permitid = models.CharField(primary_key=True, max_length=20)
    applicant = models.CharField(max_length=100)
    fooditems = models.TextField()

    def __str__(self):
        return 'Food Truck: %s, Permit: %s' % (self.applicant, self.permitid)


# Location Model
# PK:     locationid
# FK:     Truck(PK)
# Fields: 
#         lat
#         long
#         description
#         address
class Location(models.Model):
    locationid = models.IntegerField(primary_key=True)
    address = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    lat = models.FloatField()
    long = models.FloatField()
    truck = models.ForeignKey(Truck)

    def __str__(self):
        return 'Location: %s' % self.description

    # Check to see if this location is open at current time
    def isOpenNow(self): 
        curr_date = datetime.now()
        curr_time = curr_date.time()
        schedules = self.schedule_set.all()  # get all schedules
        open_now = False
        for schedule in schedules:
            # dayofweek in schedule table is 0-6 for Sun - Mon 
            # where isoweekday() by python is 1-7 for Mon - Sun
            if schedule.dayofweek == curr_date.isoweekday() % 7 :
                start_hour = int(schedule.starttime[:2])  # 11 for "11:00"
                start_min = int(schedule.starttime[3:])   # 00 for "11:00"
                end_hour = int(schedule.endtime[:2])
                end_min = int(schedule.endtime[3:])
                # time constructor can't take 24 as hour. for 24:00 we use 23:59
                if(start_hour == 24):
                    start_hour = 23
                    start_min = 59
                if(end_hour == 24):
                    end_hour = 23
                    end_min = 59
                if(curr_time >= time(start_hour,start_min) and curr_time <= time(end_hour, end_min)):
                    open_now = True
                    break
        return open_now

    # Get all schedules for today and return a sorted tuple list
    def getTodaySchedule(self):
        curr_date = datetime.now()
        schedules = self.schedule_set.all()
        ret = []
        for schedule in schedules:
            if schedule.dayofweek == curr_date.isoweekday() % 7 :
                ret.append((schedule.starttime, schedule.endtime))
        ret.sort()
        return ret 

# Schedule Model
# PK:     scheduleid
# FK1:    truck(PK:permit)
# FK2:    location(PK:location)
# Fields: 
#         dayofweek
#         starttime
#         endtime
class Schedule(models.Model):
    scheduleid = models.IntegerField(primary_key=True)
    dayofweek = models.IntegerField()
    starttime = models.CharField(max_length=5)
    endtime = models.CharField(max_length=5)
    location = models.ForeignKey(Location)
    truck = models.ForeignKey(Truck)

    def __str__(self):
        return 'dayofweek: %d, Start:  %s  End:  %s' % (self.dayofweek, self.starttime, self.endtime)

