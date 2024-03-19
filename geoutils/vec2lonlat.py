import numpy as np
def vec2lonlat(vectors):
    '''
PURPOSE

    This program converts a cartesian vector to longitude and latitude.

HISTORY

    Created by Thomas Hearty March 14, 2016

    '''

    if vectors.size == 3: #it's just one vector

        # lets first normalize it.
        vectors = vectors/np.sqrt(np.dot(vectors,vectors))

        x = vectors[0]
        y = vectors[1]
        z = vectors[2]  

        lat_rad = np.arcsin(z)
        lat = np.degrees(lat_rad)

        if x == 0.0:
           lon_rad = 0.0
        else:
           lon_rad = np.arctan(y/x)
        lon = np.degrees(lon_rad)
   
        if x < 0 and y > 0:
            lon = lon + 180
        if x < 0 and y < 0:
            lon = lon - 180

    else: #assume it's a lot of vectors

        lon = []
        lat = []
  
        for ivec in range(vectors.shape[0]):

            tmplon,tmplat = vec2lonlat(vectors[ivec,:])
            lon.append(tmplon)
            lat.append(tmplat)

        lon = np.array(lon)
        lat = np.array(lat)
          
    return lon,lat
