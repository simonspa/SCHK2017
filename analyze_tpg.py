import datetime
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime

# Relate rides with the date
ridedates = {}

with open('QV-Courses-2016-11-nm.csv', 'rb') as ridefile:
    ridereader = csv.DictReader(ridefile, delimiter=';')
    for row in ridereader:
        # Restrict to commerial rides, identified by "0"
        if row['type_course'] == 0:
            ridedates[row['course']] = row['date']


pass_per_hour = {}
pass_per_weekday = {}

with open('QV-Stops-2016-11-nm.csv', 'rb') as stopfile:
    stopsreader = csv.DictReader(stopfile, delimiter=';')
    for row in stopsreader:
        try:
            time = datetime.strptime(row['heure_depart_real'], "%H:%M:%S")
            date = datetime.strptime(,"")

            datetime.datetime.today().weekday()
            # Sum up all passengers joining a ride
            try:
                pass_per_hour[time] = pass_per_hour.get(time,0) + float(row['nb_montees'])
            except ValueError:
                print "Not a float: " + row['nb_montees']
        except ValueError:
            print "Not a time: " + row['heure_depart_real']

print random.choice(pass_per_hour.keys())

# sorted by key, return a list of tuples
plot = sorted(pass_per_hour.items())


# unpack a list of pairs into two tuples
x, y = zip(*plot) 

plt.plot(x, y)
plt.show()

