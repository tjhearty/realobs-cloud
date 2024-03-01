from tai93 import tai93_to_utc
import numpy as np
from datetime import datetime


def tai93_to_datetime(tai93_array):
    """
       This program converts an array of tai93 times to an array of utc date time structures 
    """

    dt_array = []

    for time in tai93_array:

        utc_struct = tai93_to_utc(time)
        dt = datetime(utc_struct.tm_year,utc_struct.tm_mon,utc_struct.tm_mday,utc_struct.tm_hour,utc_struct.tm_min,utc_struct.tm_sec)
        dt_array.append(dt)

    dt_array = np.array(dt_array)

    return dt_array
