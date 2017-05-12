import datetime
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime
import dateutil.parser
import json

def parse_rides():
    # Relate rides with the date

    try:
        # If JSON file exists, load and return
        with open('ridedates.json') as f:
            print "Found JSON file for rides."
            return json.load(f)
    except IOError:
        print "No JSON file for rides, parsing database."
        ridedates = {}

        with open('QV-Courses-2016-11-nm.csv', 'rb') as ridefile:
            ridereader = csv.DictReader(ridefile, delimiter=';')
            for row in ridereader:
                # Restrict to commerial rides, identified by "0"
                if int(row['type_course']) == 0:
                    ridedates[row['course']] = row['date']

            print "Found " + str(len(ridedates)) + " rides in database."

            with open('ridedates.json', 'w') as f:
                json.dump(ridedates, f)
        return ridedates

def parse_passengers(ridedates):

    try:
        # If JSON file exists, load and return
        with open('passengers_per_day.json') as f:
            print "Found JSON file for passengers."
            pass_isoday = json.load(f)
            pass_day = {}
            for key, value in pass_isoday.iteritems():
                pass_day[dateutil.parser.parse(key)] = value
            return pass_day
    except IOError:
        print "No JSON file found, parsing passenger data."
        pass_per_hour = {}
        pass_per_weekday = {}
        pass_per_day = {}

        with open('QV-Stops-2016-11-nm.csv', 'rb') as stopfile:
            stopsreader = csv.DictReader(stopfile, delimiter=';')
            for row in stopsreader:
                # Ride is only listed if commercial, so check:
                try:
                    date = datetime.strptime(ridedates[row['course']],"%Y-%m-%d")
                    try:
                        time = datetime.strptime(row['heure_depart_real'], "%H:%M:%S").replace(second=0)
                        weekday = date.weekday()

                        # Sum up all passengers joining a ride
                        try:
                            pass_per_hour[time] = pass_per_hour.get(time,0) + float(row['nb_montees'])
                            pass_per_weekday[weekday] = pass_per_weekday.get(weekday,0) + float(row['nb_montees'])
                            pass_per_day[date] = pass_per_day.get(date,0) + float(row['nb_montees'])
                        except ValueError:
                            pass
                    except ValueError:
                        pass
                except KeyError:
                    continue

        pass_isoday = {}
        for key, value in pass_per_day.iteritems():
            pass_isoday[key.isoformat()] = value

        with open('passengers_per_day.json', 'w') as f:
            json.dump(pass_isoday, f)

        return pass_per_day

def parse_rain():
    # Relate precipitation with the date

    try:
        # If JSON file exists, load and return
        with open('precipitation.json') as f:
            print "Found JSON file for precipitation."
            rain_isoday = json.load(f)
            rain_day = {}
            for key, value in rain_isoday.iteritems():
                rain_day[dateutil.parser.parse(key)] = value
            return rain_day
    except IOError:
        print "No JSON file for precipitation, parsing database."
        precipitation = {}

        with open('prec_11.dat', 'rb') as rainfile:
            precipeader = csv.DictReader(rainfile, delimiter=',')
            for row in precipeader:
                date = datetime.strptime(row['datetime'],"%Y-%m-%d %H:%M:%S").replace(hour=0,minute=0,second=0)
                precipitation[date] = precipitation.get(date, 0) + float(row['y'])

            print "Found " + str(len(precipitation)) + " rain datasets in database."

            isorain = {}
            for key, value in precipitation.iteritems():
                isorain[key.isoformat()] = value

            with open('precipitation.json', 'w') as f:
                json.dump(isorain, f)
        return precipitation


ridedates = parse_rides()
pass_per_day = parse_passengers(ridedates)
precipitation = parse_rain()

# In November 2016:
# 4x Mon, Thu, Fri, Sat, Sun
# 5x Tue, Wed
#for i, val in enumerate([4,5,5,4,4,4,4]):
#    pass_per_weekday[i] /= val


# sorted by key, return a list of tuples
#plot = sorted(pass_per_hour.items())
#plot = sorted(pass_per_weekday.items())
plot = sorted(pass_per_day.items())


# unpack a list of pairs into two tuples
x, y = zip(*plot) 

plt.plot(x, y)
plt.savefig('passengers_per_day.png')
plt.show()

