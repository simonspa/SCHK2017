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

def parse_delay(ridedates,stop,month):
    file = "json/delays-2016-" + str(month) + ".json"

    try:
        # If JSON file exists, load and return
        with open(file) as f:
            print "Found JSON file for delays."
            delay_isoday = json.load(f)
            delay_day = {}
            for key, value in delay_isoday.iteritems():
                if value > 1000:
                    continue
                delay_day[dateutil.parser.parse(key)] = value
            return delay_day
    except IOError:
        print "No JSON file found, parsing delay data."
        delay_per_day = {}
        rides_week = {}
        
        input = "QV-Stops-2016-" + str(month) + "-nm.csv"
        with open(input, 'rb') as stopfile:
            stopsreader = csv.DictReader(stopfile, delimiter=';')
            for row in stopsreader:
                # Ride is only listed if commercial, so check:
                try:
                    # Restrict to stop under investigation
                    if row['stopcode'] != stop:
                        continue

                    date = datetime.strptime(ridedates[row['course']],"%Y-%m-%d")
                    try:
                        time = datetime.strptime(row['heure_depart_real'], "%H:%M:%S").replace(minute=0,second=0)
                        date = date + timedelta(hours=time.hour)

                        try:
                            # Sum the delay of all rides passing in that hour
                            delay_per_day[date] = delay_per_day.get(date,0) + float(row['retard'])
                            rides_week[date] = rides_week.get(date,0) + 1
                        except ValueError:
                            pass
                    except ValueError:
                        pass
                except KeyError:
                    continue

        delay_isoday = {}
        for key, value in delay_per_day.iteritems():
            delay_isoday[key.isoformat()] = value / rides_week[key]

        with open(file, 'w') as f:
            json.dump(delay_isoday, f)

        return delay_per_day

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

def show_scatter(dict1,dict2,name,xl="",yl=""):
    x = []
    y = []
    for key, value in dict2.iteritems():
        x.append(dict1.get(key,0))
        y.append(value)

    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.scatter(x, y)
    plt.savefig(name)
    plt.show()


print 'Argument List:', str(sys.argv)
if len(sys.argv) == 1:
    sys.exit(0)

month = sys.argv[1]
print "Running for month " + str(month)

ridedates = parse_rides(month)
pass_per_day = parse_passengers(ridedates, month)
precipitation = parse_rain(month)
delays = parse_delay(ridedates, "CVIN18", month)

# In November 2016:
# 4x Mon, Thu, Fri, Sat, Sun
# 5x Tue, Wed
weekday_mult = []
if month == "06":
    weekday_mult = [4,4,5,5,4,4,4]
else:
    weekday_mult = [4,5,5,4,4,4,4]


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
    if key.hour < 6 or key.hour > 9:
        continue
    time = key.replace(hour=0)
    rain_day[time] = rain_day.get(time,0) + value
print "Rain data points: " + str(len(precipitation))


# Plot peak passengers per week day
peak_week = {}
for key, value in pass_day.iteritems():
    time = key.weekday()
    peak_week[time] = peak_week.get(time,0) + value

for i, val in enumerate(weekday_mult):
    peak_week[i] /= val

precip_week = {} # rain per weekday
for key, value in precipitation.iteritems():
    time = key.weekday()
    precip_week[time] = precip_week.get(time,0) + value

for i, val in enumerate(weekday_mult):
    precip_week[i] /= val

show_plot(peak_week,"peak_week_" + month + ".png","weekday","# passengers (peak)")
show_plot(precip_week,"precip_week_" + month + ".png","weekday","precipitation [mm]")
show_scatter(peak_week,precip_week,"pp_week_" + month + ".png","#p in morning peak","precipitation [mm]")



# Delay at Cornavin per weekday:
delay_week = {} # rain per weekday
for key, value in delays.iteritems():
    time = key.weekday()
    delay_week[time] = delay_week.get(time,0) + value

rides_week = {}
if month == "06":
    rides_week = {0: 1817, 1: 1827, 2: 2262, 3: 2274, 4: 1861, 5: 1237, 6: 1068}
else:
    rides_week = {0: 1809, 1: 2265, 2: 2264, 3: 1809, 4: 1852, 5: 1235, 6: 1065}

# correct for number of rides in full month on that weekday
for i, val in enumerate(weekday_mult):
    #delay_week[i] /= rides_week[i]
    delay_week[i] /= val*24

show_plot(delay_week,"delay_week_" + month + ".png","weekday","avg. delay per ride @ Cornavin [s]")


show_scatter(delays,precipitation,"delay_rain_hour_" + month + ".png","avg. delay per ride @ Cornavin [s]","precipitation [mm]")



# Mondays only
peak_monday = {}
for key, value in pass_day.iteritems():
    if(key.weekday() == 0):
        peak_monday[key] = peak_monday.get(key,0) + value
rain_monday = {}
for key, value in rain_day.iteritems():
    if(key.weekday() == 0):
        rain_monday[key] = rain_monday.get(key,0) + value
print peak_monday
print rain_monday
show_scatter(peak_monday,rain_monday,"pp_monday_" + month + ".png","#passengers (peak), Monday","precipitation in peak [mm]")



# other fun:
pass_per_hour_wk = {} # passengers over the day (hourly)
for key, value in pass_per_day.iteritems():
    if key.weekday() > 4:
        continue
    time = key.replace(year=2016,month=1,day=1)
    pass_per_hour_wk[time] = pass_per_hour_wk.get(time,0) + value
show_plot(pass_per_hour_wk,"pass_per_hour_" + month + ".png","daytime","# passengers, week")

pass_per_hour_wke = {} # passengers over the day (hourly)
for key, value in pass_per_day.iteritems():
    if key.weekday() < 5:
        continue
    time = key.replace(year=2016,month=1,day=1)
    pass_per_hour_wke[time] = pass_per_hour_wke.get(time,0) + value
show_plot(pass_per_hour_wke,"pass_per_hour_wke" + month + ".png","daytime","# passengers, weekend")



with open('passengers_per_ride.json') as f:
    pass_per_ride = json.load(f)
    plt.hist(pass_per_ride.values(),200)
    #plt.show()
