#!/usr/bin/python
import datetime
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import dateutil.parser
import json
import sys

def parse_rain():
    precipitation = {}

    with open('agrometeo-data_since2008_perHour.csv', 'rU') as rainfile:
        precipeader = csv.DictReader(rainfile, delimiter=';')
        for row in precipeader:
            date = datetime.strptime(row['datetime'],"%d.%m.%Y %H:%M").replace(minute=0,second=0)
            precipitation[date] = precipitation.get(date, 0) + float(row['y'])

        print "Found " + str(len(precipitation)) + " rain datasets in database."

        isorain = {}
        for key, value in precipitation.iteritems():
            isorain[key.isoformat()] = value

        return precipitation


def show_plot(mydict,name,xl="",yl=""):
# sorted by key, return a list of tuples
    plot = sorted(mydict.items())

    # unpack a list of pairs into two tuples
    x, y = zip(*plot)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.plot(x, y)
    plt.fill_between(x, y)
    plt.savefig(name)
    plt.show()

precipitation = parse_rain()

# preprocess rain
precip_hour = {}
for key, value in precipitation.iteritems():
    time = key.replace(year=2016,month=1,day=1)
    precip_hour[time] = precip_hour.get(time,0) + value

show_plot(precip_hour,"precip_hour_longterm.png","hour","precipitation [mm]")


precip_week = {} # rain per weekday
for key, value in precipitation.iteritems():
    time = key.weekday()
    precip_week[time] = precip_week.get(time,0) + value

show_plot(precip_week,"precip_week_longterm.png","weekday","precipitation [mm]")
