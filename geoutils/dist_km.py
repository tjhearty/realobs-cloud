import numpy as np

Rearth = 6371.0
def dist_km(lon1_deg,lat1_deg,lon2_deg,lat2_deg):
    """
PURPOSE

    This function calculates the distance in km 
    between to points on the surface of the earth given the
    longitude and latitude of the 2 points in degrees and the assumption
    that the radius of the earth is 6371 km.

HISTORY

    Created by Thomas Hearty March 14, 2016

    """
    lat1_rad = np.radians(lat1_deg)
    lon1_rad = np.radians(lon1_deg)
    lat2_rad = np.radians(lat2_deg)
    lon2_rad = np.radians(lon2_deg)

    dist_rad = np.arccos(np.cos(lat1_rad) * np.cos(lat2_rad) * np.cos(lon1_rad - lon2_rad) + np.sin(lat1_rad) * np.sin(lat2_rad))
    dist_km = Rearth * dist_rad

    return dist_km
