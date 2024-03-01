import calendar
import numpy as np
from tai93 import readleapseconds
leapseconds = readleapseconds()

def utc_to_tai93(utc):
    """converts a utc tuple to tai93 time

       One one valid point it (1993,1,1,0,0,0) which has a tai time of 0.

       Another valid point is
    """

    deltaTAI_1993_1900 = calendar.timegm((1993,1,1,0,0,0)) - calendar.timegm((1900,1,1,0,0,0)) + 27. # b/c 27 there had been 27 leap seconds by that time

    deltaNTP_utc_1900 = calendar.timegm(utc) - calendar.timegm((1900,1,1,0,0,0)) # I don't know if it is correct to call this NTP but I will

    imax = np.where(np.array(leapseconds['NTP1900']) <= deltaNTP_utc_1900)[0].max() # identify the last element that is less than or equal to the input time

    deltaTAI_utc_1900 = deltaNTP_utc_1900 + leapseconds['delta_t'][imax] # the tai time has the leap seconds

    tai93 = deltaTAI_utc_1900 - deltaTAI_1993_1900 # subtract the seconds from 1900 to 1993

    return tai93
