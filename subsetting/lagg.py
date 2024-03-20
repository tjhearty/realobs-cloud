from pydap.client import open_url
import geoutils
import numpy as np
#from opensearchtools.get_MOSurls import get_MOSurls
from opensearchtools.get_CMRgranurls import get_CMRgranurls
import h5py
import os
import urllib
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *
import myio
import requests
import tai93
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import datetime
import pdb
import time


def lagg(datasetidsandvariables,begin_date,end_date,lon=None,lat=None,radius_km=None,lonstring='Longitude',latstring='Latitude',timestring='Time',reader='h5py',usemask=True,savedownloads=False):
    """
       This will aggregate a subset of data from multiple swath files over a specified time period.  If the files are on the computer it will use them, otherwise it will ftp them.

       INPUTS (REQUIRED):

       datasetidsandvariable: A dictionary of data set ids required by OpenSearch (e.g, 'AIRX2RET.006', 'AIRX2SUP.006', 'AIRI2CCF.006') each with a corresponding list of variables.
       
       begin_date: e.g., '2015.09.01' or '2015.09.01T00:00:00Z'
       end_date: e.g, '2015.09.02' if hours minutes and seconds are not given 'T00:00:00Z' is appended.

       INPUTS (OPTIONAL):

       variables: is this is not given it will aggregate all of the variables.   

       lan, lat, radius_km: if these are not given, this it will aggregate everything

       lonstring,latstring:  if the data files have a nonstandard Longitude and Latitude name, I must specify it.

       usemask:  the default is true.  If use mask is false then the mask and the output array will be the same dimension as the input array 
       
    """

    

    datasetids = datasetidsandvariables.keys()

    tmp_string='_'.join(datasetids)+begin_date+'_'+end_date+'_'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    aggdata = {}


    for datasetid in datasetids:
        print(datasetid)
        #urls = get_MOSurls(datasetid,begin_date,end_date,lon,lat,radius_km)
        # get_CMROSurls doesn't use the datasetID, it uses the ShortName and the VersionID
        ShortName,VersionID = datasetid.split('.',1)
        ###urls,cmrxml,start_time,end_time = get_CMROSurls(ShortName,VersionID,begin_date,end_date,lon=lon,lat=lat,rad_km=radius_km)
        urls,start_time,end_time = get_CMRgranurls(ShortName,VersionID,begin_date,end_date,lon=lon,lat=lat,rad_km=radius_km)

        start_tai93 = tai93.utcstring_to_tai93(start_time)
        end_tai93 = tai93.utcstring_to_tai93(end_time)
        tmpdataset = {}   
        for variable in datasetidsandvariables[datasetid]:
            tmpdataset[variable]=np.array([]) # initiallize the numpy arrays
        if radius_km != None:
            # I will also add the distance from the center point
            tmpdataset['pointLon'] = np.array(lon) 
            tmpdataset['pointLat'] = np.array(lat) 
            tmpdataset['radius_km'] = np.array(radius_km) 
            tmpdataset['distance_km'] = np.array([]) 

        for i,url in enumerate(urls['data']):  # this version of the program downloads the original file to the local machine if it is not already there
            print(i+1,'of',len(urls['data']),url) # comment out later.  This is for diagnostic purposes to see the speed.
            
            localfile = os.environ.get('S4PA')+url.split('https:/')[1].split('.')[0]+url[url.find('.gov/')+4:] # 4: keeps the /data 9: removes it     
            if os.path.isfile(localfile): # It is mounted locally so I will not remove it.
                remove = False
            else: # I will retrieve the file and delete it when done.
                if savedownloads == True:
                    remove = False
                else:
                    remove = True


                localfile = '/tmp/'+tmp_string+os.path.basename(url)
                ####downloadfile(url,localfile)

                wget_string = 'wget --tries=100 --retry-connrefused --waitretry=6 -O '+localfile+' '+url
                print('wget_string: '+wget_string)
                os.system(wget_string)
                time.sleep(10)

            if reader == 'h5py':
                dataset = h5py.File(localfile,'r')
                datasetlon = dataset[lonstring][:]
                datasetlat = dataset[latstring][:]
                datasettime = dataset[timestring][:]

                # if radius_km == None keep the original shape and include everything
                if radius_km == None:
                    mask = np.logical_and(datasettime >= start_tai93,datasettime < end_tai93) 
                    ###for variable in datasetidsandvariables[datasetid]:
                    ###    tmpdataset[variable] = np.append(tmpdataset[variable],hdfvars.select(variable)[:])

                    for variable in datasetidsandvariables[datasetid]:
                        print(variable)
                        #if variable == 'sfcTbMWStd':
                        #    pdb.set_trace()
                        if variable in dataset.keys():
                            tmpvar = np.ma.filled(dataset[variable][:]).copy()
                        else: # assume it is vdata
                            pdb.set_trace() # the more modern datasets don't have vdata

                        if tmpvar.ndim < mask.ndim: #I'll need to replicate the variable somehow
                            if len(tmpvar) in mask.shape: # it has one of the mask dimensions
                                otherdim = set(mask.shape)-set(tmpvar.shape)
                                tmpvar2 = np.tile(tmpvar,(otherdim.pop(),1)).transpose() # this may only work for AIRS scan_node_type
                            else:
                                tmpvar2 = np.tile(tmpvar,(45,30,1))
                            tmpvar = tmpvar2.copy()


                        if usemask == True:
                            if tmpvar.ndim == mask.ndim: # if there are 2 dimensions, the following line will linearize it.
                                tmpdataset[variable] = np.append(tmpdataset[variable],tmpvar[mask])   
                            else: #then tmpvar.ndim > mask.ndim:
                                # it has at least 1 extra dimension so I will replicate the mask.  the coordinates are first
                                extradims = tmpvar.shape[len(mask.shape):]
                                n_extradims = len(extradims)
                                ###print(variable + ' has %d extra dimensions' % n_extradims)
                                if len(tmpdataset[variable]) == 0:
                                    tmpdataset[variable] = tmpvar[mask,:]
                                else:
                                    tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[mask,:]))
                        else:
                            if tmpvar.ndim == mask.ndim: 
                               if len(tmpdataset[variable]) == 0:
                                   tmpdataset[variable] = tmpvar.copy()
                               else:
                                   tmpdataset[variable] = np.vstack(tmpdataset[variable],tmpvar)   
                            else: #then tmpvar.ndim > mask.ndim:
                                # it has at least 1 extra dimension so I will replicate the mask.  the coordinates are first
                                extradims = tmpvar.shape[len(mask.shape):]
                                n_extradims = len(extradims)
                                ###print(variable + ' has %d extra dimensions' % n_extradims)
                                if len(tmpdataset[variable]) == 0:
                                    tmpdataset[variable] = tmpvar.copy()
                                else:
                                    tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar))

                else: # this will only include the data within a radius.
                    dataset_dist = geoutils.dist_km(lon,lat,datasetlon,datasetlat)
                    if dataset_dist.min() <= radius_km:
                        mask = dataset_dist <= radius_km # create the mask
                        #save the distance point is from the requested point
                        tmpdataset['distance_km']=np.append(tmpdataset['distance_km'],dataset_dist[mask])
                        #read the variables
                        for variable in datasetidsandvariables[datasetid]:
                            ###print(variable)
                            #if variable == 'sfcTbMWStd':
                            #    pdb.set_trace()
                            if variable in dataset.keys():
                                tmpvar = np.ma.filled(dataset[variable][:]).copy()
                            else: # assume it is vdata
                                pdb.set_trace() # more modern datasets don't have vdata
 
                            if tmpvar.shape == mask.shape:
                                tmpdataset[variable] = np.append(tmpdataset[variable],tmpvar[mask])   
                            else:
                               if len(tmpvar.shape) > len(mask.shape):
                                   # it has at least 1 extra dimension so I will replicate the mask.  the coordinates are first
                                   extradims = tmpvar.shape[len(mask.shape):]
                                   n_extradims = len(extradims)
                                   ###print(variable + ' has %d extra dimensions' % n_extradims)
                                   if len(tmpdataset[variable]) == 0:
                                       tmpdataset[variable] = tmpvar[mask,:]
                                   else:
                                       tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[mask,:]))
                                   ###ivalid = np.where(mask == True) 
                                   ###if len(ivalid) == 2: # I could remove this if by using ravel
                                   ###    for x,y in zip(ivalid[0],ivalid[1]):
                                   ###        if len(tmpdataset[variable]) == 0:
                                   ###            tmpdataset[variable] = tmpvar[x,y,:]
                                   ###        else:
                                   ###            tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[x,y,:]))
                                   ###else: # it must be a 1D coordinate vector 
                                   ###    for x in ivalid[0]:
                                   ###        if len(tmpdataset[variable]) == 0:
                                   ###            tmpdataset[variable] = tmpvar[x,:]
                                   ###        else:
                                   ###            tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[x,y,:]))
                                   # this is some foolishness that I don't have to do.
                                   #mask2 = np.tile(mask.reshape(mask.shape+(1,)*n_extradims),(1,)*mask.ndim+extradims)
                                   #tmpvar2 = np.tile(tmpvar,(len(dataset_dist[mask]),1))
                               else:
                                   #It's a different size array so just replicate it for every valid footprint
                                   ###if variable == 'pressStd':
                                   ###    pdb.set_trace()
                                   tmpvar2 = np.tile(tmpvar,(len(dataset_dist[mask]),1))
                                   if len(tmpdataset[variable]) == 0:
                                       tmpdataset[variable] = tmpvar2
                                   else:
                                       tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar2))
                # End of the h5py stuff

            else: # I will assume it is an hdf file
                print('reading:', localfile)
                hdfvars = SD(localfile, SDC.READ)
                dsets = hdfvars.datasets() 
                f = HDF(localfile)
                hdfvs = f.vstart()
                datasetlon = hdfvars.select(lonstring)[:]
                datasetlat = hdfvars.select(latstring)[:]
                datasettime = hdfvars.select(timestring)[:]
                # if radius_km == None keep the original shape and include everything
                if radius_km == None:
                    mask = np.logical_and(datasettime >= start_tai93,datasettime < end_tai93) 
                    ###for variable in datasetidsandvariables[datasetid]:
                    ###    tmpdataset[variable] = np.append(tmpdataset[variable],hdfvars.select(variable)[:])

                    for variable in datasetidsandvariables[datasetid]:
                        print(variable)
                        #if variable == 'sfcTbMWStd':
                        #    pdb.set_trace()
                        if variable in dsets.keys():
                            tmpvar = np.ma.filled(hdfvars.select(variable)[:]).copy()
                        else: # assume it is vdata or in a group
                            #tmpvar = np.ma.filled(hdfvs.attach(variable)[:]).flatten().copy()
                            tmpvar = hdfvs.attach(variable)[:]
                            if type(tmpvar[0][0]) is str: # I have to do this because the string is read as a long
                                tmpvar2 = []
                                for i in tmpvar:
                                    tmpvar2.append(chr(i[0]))
                                tmpvar = tmpvar2
                            tmpvar = np.ma.filled(tmpvar).flatten().copy()
 

                        if tmpvar.ndim < mask.ndim: #I'll need to replicate the variable somehow
                            if len(tmpvar) in mask.shape: # it has one of the mask dimensions
                                otherdim = set(mask.shape)-set(tmpvar.shape)
                                tmpvar2 = np.tile(tmpvar,(otherdim.pop(),1)).transpose() # this may only work for AIRS scan_node_type
                            else:
                                tmpvar2 = np.tile(tmpvar,(45,30,1))
                            tmpvar = tmpvar2.copy()


                        if usemask == True:
                            if tmpvar.ndim == mask.ndim: # if there are 2 dimensions, the following line will linearize it.
                                tmpdataset[variable] = np.append(tmpdataset[variable],tmpvar[mask])   
                            else: #then tmpvar.ndim > mask.ndim:
                                # it has at least 1 extra dimension so I will replicate the mask.  the coordinates are first
                                extradims = tmpvar.shape[len(mask.shape):]
                                n_extradims = len(extradims)
                                ###print(variable + ' has %d extra dimensions' % n_extradims)
                                if len(tmpdataset[variable]) == 0:
                                    tmpdataset[variable] = tmpvar[mask,:]
                                else:
                                    tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[mask,:]))
                        else:
                            if tmpvar.ndim == mask.ndim: 
                               if len(tmpdataset[variable]) == 0:
                                   tmpdataset[variable] = tmpvar.copy()
                               else:
                                   tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar))   
                            else: #then tmpvar.ndim > mask.ndim:
                                # it has at least 1 extra dimension so I will replicate the mask.  the coordinates are first
                                extradims = tmpvar.shape[len(mask.shape):]
                                n_extradims = len(extradims)
                                ###print(variable + ' has %d extra dimensions' % n_extradims)
                                if len(tmpdataset[variable]) == 0:
                                    tmpdataset[variable] = tmpvar.copy()
                                else:
                                    tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar))





                else: # this will only include the data within a radius.
                    dataset_dist = geoutils.dist_km(lon,lat,datasetlon,datasetlat)
                    if dataset_dist.min() <= radius_km:
                        mask = dataset_dist <= radius_km # create the mask
                        #save the distance point is from the requested point
                        tmpdataset['distance_km']=np.append(tmpdataset['distance_km'],dataset_dist[mask])
                        #read the variables
                        for variable in datasetidsandvariables[datasetid]:
                            ###print(variable)
                            #if variable == 'sfcTbMWStd':
                            #    pdb.set_trace()
                            if variable in dsets.keys():
                                tmpvar = np.ma.filled(hdfvars.select(variable)[:]).copy()
                            else: # assume it is vdata
                                tmpvar = np.ma.filled(hdfvs.attach(variable)[:]).flatten().copy()
 
                            if tmpvar.shape == mask.shape:
                                tmpdataset[variable] = np.append(tmpdataset[variable],tmpvar[mask])   
                            else:
                               if len(tmpvar.shape) > len(mask.shape):
                                   # it has at least 1 extra dimension so I will replicate the mask.  the coordinates are first
                                   extradims = tmpvar.shape[len(mask.shape):]
                                   n_extradims = len(extradims)
                                   ###print(variable + ' has %d extra dimensions' % n_extradims)
                                   if len(tmpdataset[variable]) == 0:
                                       tmpdataset[variable] = tmpvar[mask,:]
                                   else:
                                       tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[mask,:]))
                                   ###ivalid = np.where(mask == True) 
                                   ###if len(ivalid) == 2: # I could remove this if by using ravel
                                   ###    for x,y in zip(ivalid[0],ivalid[1]):
                                   ###        if len(tmpdataset[variable]) == 0:
                                   ###            tmpdataset[variable] = tmpvar[x,y,:]
                                   ###        else:
                                   ###            tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[x,y,:]))
                                   ###else: # it must be a 1D coordinate vector 
                                   ###    for x in ivalid[0]:
                                   ###        if len(tmpdataset[variable]) == 0:
                                   ###            tmpdataset[variable] = tmpvar[x,:]
                                   ###        else:
                                   ###            tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar[x,y,:]))
                                   # this is some foolishness that I don't have to do.
                                   #mask2 = np.tile(mask.reshape(mask.shape+(1,)*n_extradims),(1,)*mask.ndim+extradims)
                                   #tmpvar2 = np.tile(tmpvar,(len(dataset_dist[mask]),1))
                               else:
                                   #It's a different size array so just replicate it for every valid footprint
                                   ###if variable == 'pressStd':
                                   ###    pdb.set_trace()
                                   tmpvar2 = np.tile(tmpvar,(len(dataset_dist[mask]),1))
                                   if len(tmpdataset[variable]) == 0:
                                       tmpdataset[variable] = tmpvar2
                                   else:
                                       tmpdataset[variable] = np.vstack((tmpdataset[variable],tmpvar2))

            if remove == True:
                os.remove(localfile)
            aggdata[datasetid] = tmpdataset.copy()

    
    return aggdata




if __name__ == "__main__":

    ''' The Inputs are
        1.  location,
        2.  radius
        3.  Time range
    '''




    datasetidsandvariables={}

    #datasetidsandvariables['AIRS2RET.7.0'] = ['Longitude','Latitude','Time','TAirStd','TAirStd_QC','H2OMMRSatLevStd','H2OMMRSatLevStd_QC','RelHum','RelHum_QC','scan_node_type','pressStd','pressH2O','TSurfAir','TSurfAir_QC','TSurfStd','TSurfStd_QC','PSurfStd','PSurfStd_QC','solzen','nCld','CldFrcTot','CldFrcTot_QC','MWSurfClass','MWHingeSurfFreqGHz','EmisMWStd','EmisMWStd_QC','totH2OStd','totH2OStd_QC','SurfClass']

    #datasetidsandvariables['AIRS2CCF.7.0'] = ['Longitude','Latitude','Time','scanang']

    #datasetidsandvariables['AIRABRAD.005'] = ['Longitude','Latitude','Time','brightness_temp','scanang']

    datasetidsandvariables['AIRS2SUP.7.0'] = ['Longitude','Latitude','Time','bndry_lyr_top','bndry_lyr_top_QC']


    """
    # Begin and End Date
    begin_date = '2002.09.06T00:00:00Z'
    end_date = '2002.09.06T00:10:00Z' # note it ends at 00 UTC on this date

    outstring = '_'.join(datasetidsandvariables.keys())+'_'+begin_date+'_'+end_date

    # Porter Ranch location
    lon=-118.555
    lat=34.2961

    # Radius
    radius_km = 30.0 # km

    aggdata = lagg(datasetidsandvariables,begin_date,end_date,reader='pyhdf',usemask=False)


    myio.dict2h5(aggdata,outstring+'_lagg.h5')



    # the data can be read using the h5py library     

    aggfiledata = h5py.File('AIRX2RET.006_2002.09.06_2002.09.07_lagg.h5','r')
    """

    
    #Gulf of Mexico
    # Begin and End Date
    begin_date = '2015.10.28T10:00:00Z'
    end_date = '2015.10.29T00:00:00Z' # note it ends at 00 UTC on this date

    outstring = '_'.join(datasetidsandvariables.keys())+'_'+begin_date+'_'+end_date

    # Bounding box in the Gulf of Mexico
    lon=[-95.,-85.]
    lat=[20.,30.]

    # Radius
    #radius_km = 30.0 # km

    aggdata = lagg(datasetidsandvariables,begin_date,end_date,lon=lon,lat=lat,reader='pyhdf',usemask=False)


    myio.dict2h5(aggdata,'GulfofMexico'+outstring+'_lagg.h5')


 


    
    """
    OCO2 example

    datasetidsandvariables={}
    datasetidsandvariables['OCO2_L2_Standard.7r'] = ['/RetrievalGeometry/retrieval_longitude','/RetrievalGeometry/retrieval_latitude','/RetrievalResults/xco2','/RetrievalHeader/retrieval_time_tai93']


    # Begin and End Date
    begin_date = '2015.03.26'
    end_date = '2015.03.27' # note it ends at 00 UTC on this date


    aggdata = agg(datasetidsandvariables,begin_date,end_date,lonstring='/RetrievalGeometry/retrieval_longitude',latstring='/RetrievalGeometry/retrieval_latitude')

    """


