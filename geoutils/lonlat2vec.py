import numpy as np
import math

def lonlat2vec(lons,lats):
    '''
    This program converts a longitude and latitude to a cartesian unit vector.
    '''
    
    if type(lons).__name__ == 'float' or type(lons).__name__ == 'float64' or type(lons).__name__ == 'float32': # there is only one

        lon_rad = np.radians(lons)       #convert to radians
        lat_rad = np.radians(lats)

        x = math.cos(lon_rad) * math.cos(lat_rad)
        y = math.sin(lon_rad) * math.cos(lat_rad)
        z = math.sin(lat_rad)

        vectors = np.array([x,y,z])

    else: # we assume it is an array or list

        vectors = []

        for i in range(lons.size):

            lon = lons[i]
            lat = lats[i]
            vector = lonlat2vec(lon,lat)

            vectors.append(vector)

        vectors = np.array(vectors)

    return vectors
