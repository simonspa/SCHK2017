import datetime
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime
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


ridedates = parse_rides()

pass_per_hour = {}
pass_per_weekday = {}

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
                except ValueError:
                    pass
            except ValueError:
                pass
        except KeyError:
            continue

# In November 2016:
# 4x Mon, Thu, Fri, Sat, Sun
# 5x Tue, Wed
for i, val in enumerate([4,5,5,4,4,4,4]):
    pass_per_weekday[i] /= val


# sorted by key, return a list of tuples
#plot = sorted(pass_per_hour.items())
plot = sorted(pass_per_weekday.items())


# unpack a list of pairs into two tuples
x, y = zip(*plot) 

plt.plot(x, y)
plt.show()

