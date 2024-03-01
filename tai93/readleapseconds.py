import os
import numpy as np
import pdb
import urllib
from datetime import datetime

def readleapseconds():
    """
       Read in a list of leap seconds

       I got the list of leap seconds from the following page which provides the number of NTP seconds
       since 1900 and the used to convert between UTC and TAI:
       https://www.ietf.org/timezones/data/leap-seconds.list on how to convert from TAI to UTC.
    """

    # I will eventually want to put in some checks to make sure this file is up to date. and if not re-read it.

    
    if 'leapfile' in os.environ == False: # if it's not there I'll want to add it
        os.environ['leapfile'] = '/tmp/leap-seconds.list'

    leapsecondsfile = os.getenv('leapfile') # this environment variable should be set.

    if os.path.isfile(leapsecondsfile) == False: # If the file doesn't exist downloadit
        urllib.request.urlretrieve('https://www.ietf.org/timezones/data/leap-seconds.list',leapsecondsfile)

    f = open(leapsecondsfile, 'r')

    lines = f.read()
    f.close()
    lines = lines.split('\n')
    lines.pop()
    # the following would have the same effect
    #lines = urllib2.urlopen('https://www.ietf.org/timezones/data/leap-seconds.list').read()
    NTP1900 = []
    delta_t = []
    epoch = []
    for line in lines:
        if "File expires on" in line:
            ed = line[18:] # get the date
            edsplit = ed.split() # split the parts
            edcomma = ','.join(edsplit) # joint them with commas
            expiration_date = datetime.strptime(edcomma,'%d,%B,%Y') # Day, Month, Year
            if datetime.now() > expiration_date: #download a new leapseconds file
                urllib.request.urlretrieve('https://www.ietf.org/timezones/data/leap-seconds.list',leapsecondsfile)


    for line in lines:
        if line[0] != '#':
            NTP1900.append(float(line.split('\t')[0]))
            delta_t.append(float(line.split('\t')[1]))
            epoch.append(line.split('\t')[2])

    TAI1900 = list(np.array(NTP1900)+np.array(delta_t))

    leapseconds = {'NTP1900':NTP1900,'delta_t':delta_t,'epoch':epoch,'TAI1900':TAI1900}
    return leapseconds
