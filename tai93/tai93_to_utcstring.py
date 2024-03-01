import time
from tai93 import tai93_to_utc

def tai93_to_utcstring(tai93):
    """
       This program converts a tai93 time to a UTC time string
    """

    utc = tai93_to_utc(tai93)

    utc_string = time.strftime("%Y-%m-%dT%H:%M:%SZ", utc)

    return utc_string
