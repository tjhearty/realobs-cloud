import h5py
from pydap.client import open_url
import numpy as np
import pdb
from subprocess import call
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from netCDF4 import Dataset

import sys
import os
import math
import h5py
import urllib2
from lxml import etree

import time
import datetime
import calendar

import tai93


#import libxml2
import re
#import wget

Rearth = 6371.0
deg_to_rad = (np.pi / 180.0)

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



def vec2lonlat(vectors):
    '''
    This program converts a cartesian unit vector to longitude and latitude.
    '''

    if vectors.size == 3: #it's just one vector

        # lets first normalize it.
        vectors = vectors/np.sqrt(np.dot(vectors,vectors))

        x = vectors[0]
        y = vectors[1]
        z = vectors[2]  

        lat_rad = np.arcsin(z)
        lat = lat_rad / deg_to_rad

        if x == 0.0:
           lon_rad = 0.0
        else:
           lon_rad = np.arctan(y/x)
        lon = (lon_rad / deg_to_rad)
   
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




def dist_deg(lon1_deg,lat1_deg,lon2_deg,lat2_deg):
    """
        DIST_DEG: This function calculates the distance in degrees 
        between to points on a sphere given the longitude and latitude 
        of the 2 points in degrees.
    """
    lat1_rad = lat1_deg * deg_to_rad
    lon1_rad = lon1_deg * deg_to_rad
    lat2_rad = lat2_deg * deg_to_rad
    lon2_rad = lon2_deg * deg_to_rad

    dist = np.arccos(np.cos(lat1_rad) * np.cos(lat2_rad) * np.cos(lon1_rad - lon2_rad) + np.sin(lat1_rad) * np.sin(lat2_rad))
    dist_deg_out = dist / deg_to_rad


    return dist_deg_out



def dist_km(lon1_deg,lat1_deg,lon2_deg,lat2_deg):
    """
        DIST_km: This function calculates the distance in km 
        between to points on the surface of the earth given the
        longitude and latitude of the 2 points in degrees and the assumption
        that the radius of the earth is 
    """
    lat1_rad = lat1_deg * deg_to_rad
    lon1_rad = lon1_deg * deg_to_rad
    lat2_rad = lat2_deg * deg_to_rad
    lon2_rad = lon2_deg * deg_to_rad

    dist_rad = np.arccos(np.cos(lat1_rad) * np.cos(lat2_rad) * np.cos(lon1_rad - lon2_rad) + np.sin(lat1_rad) * np.sin(lat2_rad))
    dist_km = Rearth * dist_rad


    return dist_km


def r2bb(clon,clat,rad_km):
    """
       Convert a point and a radius to a bounding box
    """

    # Convert the location to a vector
    location_vector = Rearth * lonlat2vec(clon,clat)

    north_vector = Rearth * lonlat2vec(0.,90.)


    bbn = north_vector - location_vector
    bbn = radius_km * (bbn/np.sqrt(np.dot(bbn,bbn))) # renormalize this vector to be the radius

    # the cross product of the location_vector with the north_vector points west.
    bbw = np.cross(location_vector,north_vector)
    bbw = radius_km * (bbw/np.sqrt(np.dot(bbw,bbw))) # renormalize this vector to be the radius

    # the lower left positon is 
    ll = location_vector + bbw - bbn
    ur = location_vector - bbw + bbn

    ll_lon,ll_lat = vec2lonlat(ll)
    ur_lon,ur_lat = vec2lonlat(ur)

    return (ll_lon,ll_lat,ur_lon,ur_lat) # (lllon, lllat, urlon, urllat)




def get_opendapurls(dataset,begin_date,end_date,lon=None,lat=None,rad_km=None):
    """
       Return a list of opendap urls given the above input parameters.  It will convert the radius to bounding box centered on the given longitude and latitude
    """
    begin_date = begin_date.replace('.','-')
    end_date = end_date.replace('.','-')

    if len(begin_date) == 10:
        date_string = "startTime="+begin_date+"T00:00:00Z&endTime="+end_date+"T00:00:00Z&"
    else:
        date_string = "startTime="+begin_date+"&endTime="+end_date+"&"  


    if rad_km is None:
        bb_string=''
    else:
        bb = r2bb(lon,lat,rad_km) # bounding box tuple
        bb_string = "osLocation="+str(bb[0])+','+str(bb[1])+','+str(bb[2])+','+str(bb[3])+"&"

    opensearch_string = "http://mirador.gsfc.nasa.gov/cgi-bin/mirador/granlist.pl?" \
    "searchType=Nominal&format=atom&" \
    +date_string+bb_string+"maxgranules=5000000&dataSet="+dataset

    #wget_string = 'wget -q "http://mirador.gsfc.nasa.gov/cgi-bin/mirador/granlist.pl?searchType=Nominal&format=atom&startTime=%sT00:00:00Z&endTime=%sT00:00:00Z&osLocation=%f,%f,%f,%f&maxgranules=10000000&dataSet=AIRX2RET.006" -O -' % (begin_date,end_date,ll_lon,ll_lat,ur_lon,ur_lat)

    search_results = urllib2.urlopen(opensearch_string).read()

    opendapurls = re.findall('\S+/opendap/.+hdf.html\S+',search_results)

    for i,url in enumerate(opendapurls):
        newurl = url.replace('href="','').replace('.html"/>','')
        opendapurls[i] = newurl

    opendapurls = list(set(opendapurls)) # makes them unique and sorts them

    opendapurls.sort() # this will probably put them in chronological order but it must be verified.

    return opendapurls




def get_dataurls(dataset,begin_date,end_date,lon=None,lat=None,rad_km=None):
    """
       Return a list of data set urls given the above input parameters.  It will convert the radius to bounding box centered on the given longitude and latitude
    """
    begin_date = begin_date.replace('.','-')
    end_date = end_date.replace('.','-')

    if len(begin_date) == 10:
        date_string = "startTime="+begin_date+"T00:00:00Z&endTime="+end_date+"T00:00:00Z&"
    else:
        date_string = "startTime="+begin_date+"&endTime="+end_date+"&"  


    if rad_km is None:
        bb_string=''
    else:
        bb = r2bb(lon,lat,rad_km) # bounding box tuple
        bb_string = "osLocation="+str(bb[0])+','+str(bb[1])+','+str(bb[2])+','+str(bb[3])+"&"

    opensearch_string = "http://mirador.gsfc.nasa.gov/cgi-bin/mirador/granlist.pl?" \
    "searchType=Nominal&format=atom&" \
    +date_string+bb_string+"maxgranules=5000000&dataSet="+dataset


    #wget_string = 'wget -q "http://mirador.gsfc.nasa.gov/cgi-bin/mirador/granlist.pl?searchType=Nominal&format=atom&startTime=%sT00:00:00Z&endTime=%sT00:00:00Z&osLocation=%f,%f,%f,%f&maxgranules=10000000&dataSet=AIRX2RET.006" -O -' % (begin_date,end_date,ll_lon,ll_lat,ur_lon,ur_lat)

    search_results = urllib2.urlopen(opensearch_string).read()



    opendapurls = re.findall('\S+/data/s4pa/.+hdf.html\S+',search_results)

    for i,url in enumerate(opendapurls):
        newurl = url.replace('href="','').replace('.html"/>','')
        opendapurls[i] = newurl

    opendapurls = list(set(opendapurls)) # makes them unique and sorts them

    opendapurls.sort() # this will probably put them in chronological order but it must be verified.

    return opendapurls















def sim_sat(SATcoords,MERRAShortName,variables):
    """
       Inputs:
           SATcoords: a dictionary of Satellite Lon, Lat, and Time
           MERRAShortName: The MERRA short name from which to get the variables.
           variables: a list of strings containing the MERRA variables to include.
       Outputs:
           SSSMdata: a dictionary containing the MERRA Data sampled like Satellite Level 2
    """

    start_time = tai93_to_utcstring(np.array(SATcoords['Time']).min())
    end_time = tai93_to_utcstring(np.array(SATcoords['Time']).max())


    merra_urls = get_opendapurls(MERRAShortName,start_time,end_time)

    data_urls = get_dataurls(MERRAShortName,start_time,end_time)

    pdb.set_trace()

    return SSSMdata











if __name__ == "__main__":

    ''' The Inputs are
        1.  location,
        2.  radius
        3.  Time range'''


    dataset='AIRX2RET.006'

    # Begin and End Date
    begin_date = '2015.09.01'
    end_date = '2015.09.02' # note it ends at 00 UTC on this date

    # NOAA Summit Station
    NOAALon = -38.48 
    NOAALat = 72.58

    # GCNet Summit Station
    GCNetLon = -38.50
    GCNetLat = 72.5794

    # Average Summit location
    lon=np.mean([NOAALon,GCNetLon])
    lat=np.mean([NOAALat,GCNetLat])

    # Radius
    radius_km = 30.0 # km

    # define the leap seconds globally
    readleapseconds()


    stdopendap_urls = get_opendapurls('AIRX2RET.006',begin_date,end_date,lon,lat,radius_km)
    supopendap_urls = get_opendapurls('AIRX2SUP.006',begin_date,end_date,lon,lat,radius_km)
    ccopendap_urls = get_opendapurls('AIRI2CCF.006',begin_date,end_date,lon,lat,radius_km)


    merra_urls = get_dataurls('M2T1NXSLV.5.12.4','2002.09.06','2002.09.07')

    pdb.set_trace()
  
    #grep 'OPeNDAP HTML' | egrep -o 'href=\".*h5.html\"' | egrep -o 'http.*html' > my_list.txt'


    ###dataset = open_url(opendapurl)


    ###keys = dataset.keys() # gets the keys


    # I will play with time here:
    stdopendap_url = stdopendap_urls[0]
    stddataset = open_url(stdopendap_url)
    start_Time = stddataset['start_Time'].data[:]

    for stdopendap_url in stdopendap_urls:
        
        stddataset = open_url(stdopendap_url)   

        stdLongitude = stddataset['Longitude'].data[:]
        stdLatitude = stddataset['Latitude'].data[:]
        stdTime = stddataset['Time'].data[:]
        


        airscoords = {'Lon':stdLongitude,'Lat':stdLatitude,'Time':stdTime}

        pdb.set_trace()

        readleapseconds()


        MSAL2data = sim_sat(airscoords,'M2T1NXSLV.5.12.4',['TS','T2M','T10M','TROPPT'])

        SATcoords = airscoords
        MERRAShortName = 'M2T1NXSLV.5.12.4'
        variables = ['TS','T2M','T10M','TROPPT']


        fp_dist_km = dist_km(Longitude,Latitude,lon,lat)

        validmask2d = fp_dist_km <= radius_km
   

        # get the variables the satisfy the condition

        selTime = dataset['Time'].data[:][validmask2d]

        
