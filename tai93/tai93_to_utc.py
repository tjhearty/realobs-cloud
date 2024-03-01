import time
import calendar
from tai93 import readleapseconds
leapseconds = readleapseconds()
import numpy as np


def tai93_to_utc(tai93):
    """
       This program converts a tai93 time to a UTC time tuple 
    """

    tai70 = tai93 + calendar.timegm((1993,1,1,0,0,0)) + 27.0 # the +27 is because of the epoc for 1993

    tai1900 = tai70 - calendar.timegm((1900,1,1,0,0,0))

    imax = np.where(np.array(leapseconds['TAI1900']) <= tai1900)[0].max()

    ntp70 = tai70 - leapseconds['delta_t'][imax]

    utc = time.gmtime(ntp70)

    return utc
