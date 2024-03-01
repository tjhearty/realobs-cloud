import time
from tai93.utc_to_tai93 import utc_to_tai93
import pdb

def utcstring_to_tai93(utc_string):
    """
       This program converts a UTC time string to tai93
    """

    utc = time.strptime(utc_string,"%Y-%m-%dT%H:%M:%SZ")

    tai93 = utc_to_tai93(utc)

    return tai93
