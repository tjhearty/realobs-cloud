import numpy as np
def dist_deg(lon1_deg,lat1_deg,lon2_deg,lat2_deg):
    """

PURPOSE

    This function calculates the distance in degrees 
    between to points on a sphere given the longitude and latitude 
    of the 2 points in degrees.

HISTORY

    Created by Thomas Hearty March 14, 2016

    """
    lat1_rad = np.radians(lat1_deg)
    lon1_rad = np.radians(lon1_deg)
    lat2_rad = np.radians(lat2_deg)
    lon2_rad = np.radians(lon2_deg)

    dist = np.arccos(np.cos(lat1_rad) * np.cos(lat2_rad) * np.cos(lon1_rad - lon2_rad) + np.sin(lat1_rad) * np.sin(lat2_rad))
    dist_deg_out = np.degrees(dist)


    return dist_deg_out
