Rearth = 6371.0
import numpy as np
from geoutils import vec2lonlat,lonlat2vec

def r2bb(clon,clat,rad_km):
    """
PURPOSE

    Convert a point and a radius to a bounding box

HISTORY

    Created by Thomas Hearty March 14, 2016

    """

    # Convert the location to a vector
    location_vector = Rearth * lonlat2vec(clon,clat)

    north_vector = Rearth * lonlat2vec(0.,90.)


    bbn = north_vector - location_vector
    bbn = rad_km * (bbn/np.sqrt(np.dot(bbn,bbn))) # renormalize this vector to be the radius

    # the cross product of the location_vector with the north_vector points west.
    bbw = np.cross(location_vector,north_vector)
    bbw = rad_km * (bbw/np.sqrt(np.dot(bbw,bbw))) # renormalize this vector to be the radius

    # the lower left positon is 
    ll = location_vector + bbw - bbn
    ur = location_vector - bbw + bbn

    ll_lon,ll_lat = vec2lonlat(ll)
    ur_lon,ur_lat = vec2lonlat(ur)

    return (ll_lon,ll_lat,ur_lon,ur_lat) # (lllon, lllat, urlon, urllat)

