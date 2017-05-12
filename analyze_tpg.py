#!/usr/bin/python
import datetime
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import dateutil.parser
import json
import sys

def parse_rides(month):
    # Relate rides with the date
    file = "json/ridedates-2016-" + str(month) + ".json"

    try:
        # If JSON file exists, load and return
        with open(file) as f:
            print "Found JSON file for rides."
            return json.load(f)
    except IOError:
        print "No JSON file for rides, parsing database."
        ridedates = {}

        input = "QV-Courses-2016-" + str(month) + "-nm.csv"
        with open(input, 'rb') as ridefile:
            ridereader = csv.DictReader(ridefile, delimiter=';')
            for row in ridereader:
                # Restrict to commerial rides, identified by "0"
                if int(row['type_course']) == 0:
                    ridedates[row['course']] = row['date']

            print "Found " + str(len(ridedates)) + " rides in database."

            with open(file, 'w') as f:
                json.dump(ridedates, f)
        return ridedates

def parse_passengers(ridedates,month):
    file = "json/passengers-2016-" + str(month) + ".json"

    try:
        # If JSON file exists, load and return
        with open(file) as f:
            print "Found JSON file for passengers."
            pass_isoday = json.load(f)
            pass_day = {}
            for key, value in pass_isoday.iteritems():
                pass_day[dateutil.parser.parse(key)] = value
            return pass_day
    except IOError:
        print "No JSON file found, parsing passenger data."
        pass_per_day = {}
        total_per_ride = {}

        input = "QV-Stops-2016-" + str(month) + "-nm.csv"
        with open(input, 'rb') as stopfile:
            stopsreader = csv.DictReader(stopfile, delimiter=';')
            for row in stopsreader:
                # Ride is only listed if commercial, so check:
                try:
                    date = datetime.strptime(ridedates[row['course']],"%Y-%m-%d")
                    try:
                        time = datetime.strptime(row['heure_depart_real'], "%H:%M:%S").replace(minute=0,second=0)
                        date = date + timedelta(hours=time.hour)

                        # Sum up all passengers joining a ride
                        try:
                            pass_per_day[date] = pass_per_day.get(date,0) + float(row['nb_montees'])
                            total_per_ride[row['course']] = total_per_ride.get(row['course'],0) + float(row['nb_montees']) - float(row['nb_descentes'])
                        except ValueError:
                            pass
                    except ValueError:
                        pass
                except KeyError:
                    continue

        pass_isoday = {}
        for key, value in pass_per_day.iteritems():
            pass_isoday[key.isoformat()] = value

        with open(file, 'w') as f:
            json.dump(pass_isoday, f)

        with open('passengers_per_ride.json', 'w') as f:
            json.dump(total_per_ride, f)

        return pass_per_day

def parse_rain(month):
    # Relate precipitation with the date
    file = "json/precipitation-2016-" + str(month) + ".json"

    try:
        # If JSON file exists, load and return
        with open(file) as f:
            print "Found JSON file for precipitation."
            rain_isoday = json.load(f)
            rain_day = {}
            for key, value in rain_isoday.iteritems():
                rain_day[dateutil.parser.parse(key)] = value
            return rain_day
    except IOError:
        print "No JSON file for precipitation, parsing database."
        precipitation = {}

        input = "prec_" + str(month) + ".dat"
        with open(input, 'rb') as rainfile:
        #with open('agrometeo-data-since2008.csv', 'rU') as rainfile:
            precipeader = csv.DictReader(rainfile, delimiter=',')
            for row in precipeader:
                date = datetime.strptime(row['datetime'],"%Y-%m-%d %H:%M:%S").replace(minute=0,second=0)
                #date = datetime.strptime(row['datetime'],"%d.%m.%Y").replace(minute=0,second=0)
                precipitation[date] = precipitation.get(date, 0) + float(row['y'])

            print "Found " + str(len(precipitation)) + " rain datasets in database."

            isorain = {}
            for key, value in precipitation.iteritems():
                isorain[key.isoformat()] = value

            with open(file, 'w') as f:
                json.dump(isorain, f)
        return precipitation

print 'Argument List:', str(sys.argv)
if len(sys.argv) == 1:
    sys.exit(0)

month = sys.argv[1]
print "Running for month " + str(month)

ridedates = parse_rides(month)
pass_per_day = parse_passengers(ridedates, month)
precipitation = parse_rain(month)

# In November 2016:
# 4x Mon, Thu, Fri, Sat, Sun
# 5x Tue, Wed
#for i, val in enumerate([4,5,5,4,4,4,4]):
#    pass_per_weekday[i] /= val

# preprocess passengers:
pass_day = {}
for key, value in pass_per_day.iteritems():
    if key.hour < 6 or key.hour > 9:
        continue
    time = key.replace(hour=0)
    pass_day[time] = pass_day.get(time,0) + value
print "Passenger points: " + str(len(pass_day))

# preprocess rain
rain_day = {}
for key, value in precipitation.iteritems():
    time = key.replace(hour=0)
    rain_day[time] = rain_day.get(time,0) + value
print "Rain data points: " + str(len(precipitation))


x = []
y = []
for key, value in rain_day.iteritems():
    if key.weekday() == 5 or key.weekday() == 6:
        continue
    x.append(pass_day.get(key,0))
    y.append(value)


plt.scatter(x, y)
plt.show()

# other fun:
pass_per_hour = {} # passengers over the day (hourly)
for key, value in pass_per_day.iteritems():
    time = key.replace(year=2016,month=1,day=1)
    pass_per_hour[time] = pass_per_hour.get(time,0) + value
precip_week = {} # rain per weekday
for key, value in precipitation.iteritems():
    time = key.weekday()
    precip_week[time] = precip_week.get(time,0) + value


# sorted by key, return a list of tuples
#plot = sorted(pass_per_hour.items())
#plot = sorted(pass_per_weekday.items())
#plot = sorted(pass_per_day.items())
#plot = sorted(precipitation.items())
plot = sorted(precip_week.items())

# unpack a list of pairs into two tuples
x, y = zip(*plot) 


plt.plot(x, y)
plt.fill_between(x, y)
plt.ylim(0.0, plt.ylim()[1]+50)
plt.xlim(0, 6)
#plt.savefig('passengers_per_day.png')
plt.show()


