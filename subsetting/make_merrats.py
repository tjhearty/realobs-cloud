from pydap.client import open_url
#from opensearchtools.get_MOSurls import get_MOSurls
from opensearchtools.get_CMROSurls import get_CMROSurls
import numpy as np
import tai93
import datetime
import pdb

def make_merrats(datasetid,begin_date,end_date,lon,lat,variables):
    """
    This program extracts a time series of MERRA data that is nearest to a given point
    """
    #### turn this into a program to get MERRA Timeseries that works for MERRA and MERRA2


    if datasetid[0:2] == 'M2':  # these are the MERRA2 conventions for time and location
        lonstring = 'lon'
        latstring = 'lat'
        timestring = 'time'
    else: # these are the MERRA conventions for time and location
        lonstring = 'XDim'
        latstring = 'YDim'
        timestring = 'TIME'

    #merra_urls = get_MOSurls(datasetid,begin_date,end_date,urltype='data')
    # get_CMROSurls doesn't use the datasetID, it uses the ShortName and the VersionID
    ShortName,VersionID = datasetid.split('.')
    merra_urls,cmrxml,start_time,end_time = get_CMROSurls(ShortName,VersionID,begin_date,end_date,lon,lat,radius_km)



    
    for i in range(len(merra_urls)): 
        merra_urls[i] = merra_urls[i].replace('data/s4pa//','opendap/')
    for i in range(len(merra_urls)): 
        merra_urls[i] = merra_urls[i].replace('data//','opendap/')

    merradataset = open_url(merra_urls[0])

    merra_lon = merradataset[lonstring][:]
    merra_lat = merradataset[latstring][:]


    im_lon = np.abs(lon-merra_lon).argmin()
    im_lat = np.abs(lat-merra_lat).argmin()

    tsdata = {}
    tmpvar = np.array([])
    
    for variable in variables:
        tsdata[variable] = tmpvar.copy()

    tsdata['Time'] = tmpvar.copy()

    tsdata['lon'] = lon
    tsdata['lat'] = lat

    for i, merra_url in enumerate(merra_urls): 
        merradataset = open_url(merra_url)
       
        merra_time = merradataset[timestring][:] # minutes since the start of the day
        merra_begin_date = merradataset[timestring].attributes['begin_date']
        merra_begin_time = merradataset[timestring].attributes['begin_time']

        # Get the UTC at the start of the granule
        merra_begin_utc = (int(str(merra_begin_date)[0:4]), int(str(merra_begin_date)[4:6]), int(str(merra_begin_date)[6:]), 0, int(str(merra_begin_time)[0:2]), int(str(merra_begin_time)[2:]))

        # convert the begin time to tai93
        merra_begin_tai93 = tai93.utc_to_tai93(merra_begin_utc)

        # get the tai93 for each time step.  Remember that for MERRA "time" is minutes since the begin_time
        merra_tai93 = merra_begin_tai93 + merra_time * 60.0
 
        tsdata['Time'] = np.hstack((tsdata['Time'],merra_tai93))

        for variable in variables:
            tsdata[variable] = np.hstack((tsdata[variable],merradataset[variable][0,im_lat,im_lon].ravel())) # Why do they do this?

    # I need to sort the requested variables by time because the OpenSearch results are not necessarily sorted.

    isort = tsdata['Time'].argsort()
    
    for variable in variables:
        tsdata[variable] = tsdata[variable][isort]

    # I need to sort the time after the other variables because after it's been sorted it can be used to sort the 
    tsdata['Time'] = tsdata['Time'][isort]



    return tsdata


if __name__ == "__main__":

    '''
    This is just some code to test get_MOSurls.py.
    '''

    # NOAA Summit Station
    NOAALon = -38.48 
    NOAALat = 72.58

    # GCNet Summit Station
    ###GCNetLon = -38.50
    ###GCNetLat = 72.5794

    # Average Summit location
    lon=NOAALon
    lat=NOAALat

    variables = ['TS','T2M','T10M']

    tsdata = make_merrats('MATMNXSLV.5.2.0','2002.09.01','2003.04.01',lon,lat,variables)


