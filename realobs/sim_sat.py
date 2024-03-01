from pydap.client import open_url
from pydap.cas.urs import setup_session
import netrc
import tai93
import numpy as np
###from opensearchtools.get_MOSurls import get_MOSurls
from opensearchtools.get_CMRgranurls import get_CMRgranurls
from netCDF4 import Dataset

import datetime
import itertools
import os
import urllib
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *

# the next imports can be removed when put into ops.
import pdb
import h5py
import myio
from subsetting import lagg
from netCDF4 import num2date, date2num

import cdsapi # I need this to get ERA5 data.
import mytime # I also use this to get ERA5 data.
import realobs

def sim_sat(SATcoords,ShortName,VersionID,variables,reader='opendap'):
    """
       Inputs:
           SATcoords: a dictionary of Satellite Lon, Lat, and Time
           ShortName: The short name from which to get the variables.
           variables: a list of strings containing the MERRA variables to include.
           reader: choices are opendap (default), pyhdf, h5py, or netcdf4
       Outputs:
           SSSdata: a dictionary containing the MERRA Data sampled like Satellite Level 2
    """

    # get the start and stop times.
    start_time = tai93.tai93_to_utcstring(np.array(SATcoords['time']).min())
    end_time = tai93.tai93_to_utcstring(np.array(SATcoords['time']).max())


    if ShortName[0:2] == 'M2':  # these are the MERRA2 conventions for time and location
        lonstring = 'lon'
        latstring = 'lat'
        timestring = 'time'
        levstring = 'lev'
    elif ShortName[0:2] == 'ER': # these are the ERA conventions
        lonstring = 'longitude'
        latstring = 'latitude'
        timestring = 'time'
        levstring = 'level'
    else: # this is MERRA stuff
        lonstring = 'XDim'
        latstring = 'YDim'
        timestring = 'TIME'
        levstring = 'Height' # it may not be called this in merra!!!


    if ShortName[0:1] == 'M': 
        # find the MERRA urls
        
        urls,start_time,end_time = get_CMRgranurls(ShortName,VersionID,start_time,end_time)
        #dataurls = get_MOSurls(ShortName,start_time,end_time)

        if reader == 'opendap':
            dataurls = urls['opendap'].copy()
        else:
            dataurls = urls['data'].copy()
            
        dataurls.sort() # I don't know why I had to sort this before?
        

    else: # get the ecmwf file

        # I'll just keep the files local from now on.
        ###if os.path.isdir('/run/media/thearty/backup3TB'):
        ###    eradir =  '/run/media/thearty/backup3TB/data/ERA5/'
        ###else:
        datadir = os.environ.get("DATADIR")
        eradir = datadir+'/ERA5/'

        dataurls = [eradir+'TqRH'+''.join(start_time[0:10].split('-'))+'.nc',eradir+'TqRH'+''.join(end_time[0:10].split('-'))+'.nc']
        dataurls = list(set(dataurls)) # this gets the unique values.
        dataurls.sort() # I don't know why I had to sort this before?

        for url in dataurls:
            if os.path.exists(url) == False: # if the ERA5 file does not exist I will have to get it.
                date_string = url.split('TqRH')[-1].split('.')[0]
                date_string = date_string[0:4] + '.' + date_string[4:6] + '.' + date_string[6:] # change the format to include .s
                # also change the eradir to a local directory so that it runs faster:
                localfiles = realobs.get_ecmwf(date_string,date_string,outdir=eradir)


  
    if reader == 'netcdf4' : # the files are local
            print('I assume that the files are local.')



    # create the output dictionary and fill it with dummy variables
    SSSdata = {} # this will be the output dictionary
    # for vertical or higher dim variables (temperature and water vapor) I will need to add more dims
    tmpvar = np.ones(SATcoords['time'].shape)*-9999.0

    ### I will have to put the following inside the loop.  So rather than defing the elements of the structure beforehand I'll just see if theive been defined yet.
    '''
    for variable in variables:
        if MERRAdata[variable].ndim == 3: 
            SSSdata[variable] = tmpvar.copy()
        else:
            tmpvar2 = np.repeat(np.expand_dims(tmpvar,tmpvar.ndim),merra_lev.size,axis=tmpvar.ndim)
            SSSdata[variable] = tmpvar2.copy()
    '''

    # it only takes the first one.  What if there are two?
    for dataurl in dataurls:
        print('Opening: '+dataurl)
        if reader == 'opendap':
            # this is how to get the username and password from the .netrc file
            netrc.netrc().authenticators('urs.earthdata.nasa.gov')
            username = netrc.netrc().authenticators('urs.earthdata.nasa.gov')[0]
            password = netrc.netrc().authenticators('urs.earthdata.nasa.gov')[2]
            session = setup_session(username, password,check_url=dataurl) # setup the opendap connection
            merradataset = open_url(dataurl, session=session)
            ra_lon = merradataset[lonstring][:]
            ra_lat = merradataset[latstring][:]
            ra_time = merradataset[timestring][:] # minutes since the start of the day
            if levstring in merradataset.keys():
                ra_lev = merradataset[levstring][:]
            #else:
            #    ra_lev = None

            ra_begin_date = merradataset[timestring].attributes['begin_date']
            ra_begin_time = merradataset[timestring].attributes['begin_time']
            REALObsdata = {}
            for variable in variables:
                # this part will read the MERRA data for this day.

                REALObsdata[variable] = merradataset[variable][:]

                # this part will only be executed if the output structure has not been initialized so it should
                # only be executed the first time.
                if variable not in SSSdata.keys():
                    if REALObsdata[variable].ndim == 3: # I might have to change this back to == 3 if it doesn't work for 4
                        SSSdata[variable] = tmpvar.copy()
                    else:
                        tmpvar2 = np.repeat(np.expand_dims(tmpvar,tmpvar.ndim),ra_lev.size,axis=tmpvar.ndim)
                        SSSdata[variable] = tmpvar2.copy()


        else:
            # get a local copy

            if os.path.exists(dataurl): # the file already exists locally
                localfile = dataurl        
            else:
                localfile = '/tmp/'+os.path.basename(dataurl)
                #urllib.request.urlretrieve(dataurl,localfile) # I'll use wget instead of this
                os.system('wget -O '+localfile+' '+dataurl)


            if reader == 'h5py': # I'll add this later. It might work for netcdf4 or I can use a netcdf4 reader
                merradataset = h5py.File(localfile,'r')
                
            if reader == 'pyhdf':
                hdfvars = SD(localfile, SDC.READ)
                dsets = hdfvars.datasets() 
                attr = hdfvars.attributes(full=1)
                f = HDF(localfile)
                hdfvs = f.vstart()
                ra_lon = hdfvars.select(lonstring)[:]
                ra_lat = hdfvars.select(latstring)[:]
                ra_time = hdfvars.select(timestring+':EOSGRID')[:] # the :EOSGRID is hdf4 weirdness
                ra_begin_date = hdfvars.select(timestring+':EOSGRID').attributes()['begin_date']
                ra_begin_time = hdfvars.select(timestring+':EOSGRID').attributes()['begin_time']
                REALObsdata = {}
                for variable in variables:
                    REALObsdata[variable] = hdfvars.select(variable)[:]
                os.remove(localfile)

            if reader == 'netcdf4':

                data = Dataset(localfile,'r') # these are the 3d variables

                ra_lon = data.variables[lonstring][:]

                # covert any longitudes >= 180 to a 
                highlons = ra_lon > 180.
                ra_lon[highlons] = ra_lon[highlons] - 360.0

                ra_lat = data.variables[latstring][:]

                ra_time = data.variables[timestring] # hours since 1900-01-01T00:00:00.0
                ra_dates = num2date(ra_time[:], units = ra_time.units) # I used to have to specify the calendar now it assumes Gregorian
                #ra_dates = num2date(ra_time[:], units = ra_time.units,calendar = ra_time.calendar)
                if levstring in data.variables.keys():
                    ra_lev = data.variables[levstring][:]
                #else:
                #    ra_lev = None

                twodfile = localfile.replace('TqRH','SurfacePressure') # this is the surface pressure file
                twoddata = Dataset(twodfile,'r') # these are the 2d variables assuming it's ECMWF.
                ra_begin_time = ra_time[0] # this is hours since 1900-01-01T00:00:00.0.  I may need tai93.

                REALObsdata = {}
                for variable in variables:
                    # this part will read the Reanalysis data for this day.

                    if variable == 'sp': #it's a 2d variable from the 
                        REALObsdata[variable] = twoddata.variables[variable][:]
                    else: # it's a 3d variable.
                        REALObsdata[variable] = data.variables[variable][:]


                    # this part will only be executed if the output structure has not been initialized so it should
                    # only be executed the first time.
                    if variable not in SSSdata.keys():
                        if REALObsdata[variable].ndim == 3:  #this is actually 2 spatial dims + time
                            SSSdata[variable] = tmpvar.copy()
                        else:
                            tmpvar2 = np.repeat(np.expand_dims(tmpvar,tmpvar.ndim),ra_lev.size,axis=tmpvar.ndim)
                            SSSdata[variable] = tmpvar2.copy()

                # I'll close the files because this may cause some memory problem on the computer.
                # I commented this out becuase deleting the file seems to have cause a problem
                ###data.close()
                ###twoddata.close()

                ###for tmpfile in [localfile,twodfile]:
                ###    os.remove(tmpfile)



        # read in the MERRA data  !!!! I don't need this step anymore.  See merradataset[variable][im_time,im_lat,im_lon].flatten()[0]!!!
        # But I still don't know how to do this for a level quantity.

        ###pdb.set_trace()

        # Get the UTC at the start of the granule

        if ShortName[0:1] == 'M':

            # I need to create a utc tuple to convert to tai93 time
            if ra_begin_time == 0:
                ra_begin_utc = (int(str(ra_begin_date)[0:4]), int(str(ra_begin_date)[4:6]), int(str(ra_begin_date)[6:]), \
                                   0, 0, 0)
            else:
                ra_begin_utc = (int(str(ra_begin_date)[0:4]), int(str(ra_begin_date)[4:6]), int(str(ra_begin_date)[6:]), \
                                   0, int(str(ra_begin_time)[0:2]), int(str(ra_begin_time)[2:]))
        else: #I'll assume it's ecmwf
            ra_begin_utc = (ra_dates[0].year, ra_dates[0].month, ra_dates[0].day, ra_dates[0].hour, ra_dates[0].minute, ra_dates[0].second)


        # convert the begin time to tai93
        ra_begin_tai93 = tai93.utc_to_tai93(ra_begin_utc)

        # convert the end time to tai93.  I am assuming daily files here so the end time is 1 day or 24 hours after the begin time
        ###I do this by creating a date time object and the giving utc_to_tai93 a utctimetuple.

        ra_end_utc_object = datetime.datetime(ra_begin_utc[0],ra_begin_utc[1],ra_begin_utc[2],ra_begin_utc[3],ra_begin_utc[4],ra_begin_utc[5]) + datetime.timedelta(days=1) 
        ra_end_tai93 = tai93.utc_to_tai93(ra_end_utc_object.utctimetuple())

        # get the tai93 for each time step.  Remember that for MERRA "time" is minutes since the begin_time
        if ShortName[0:1] == 'M': # assume it's MERRA
            ra_tai93 = ra_begin_tai93 + ra_time.data * 60.0
        else: # assume it's ecmwf
            ra_tai93 = []
            for date in ra_dates:
                ra_tai93.append(tai93.utc_to_tai93((date.year,date.month,date.day,date.hour,date.minute,date.second)))
            ra_tai93 = np.array(ra_tai93) # convert this to an array.

        ra_time_inc = ra_tai93[1] - ra_tai93[0]

        SATtimes = SATcoords['time'].ravel()
            

        # I used to define the SSSdata here but it should be outside of the url loop.

        print('Filling SSSdata for ', dataurl)
        for i, (SATlon,SATlat,SATtime) in enumerate(zip(SATcoords['lon'].ravel(),SATcoords['lat'].ravel(),SATcoords['time'].ravel())):
            if SATtime >= ra_begin_tai93-(ra_time_inc/2.) and SATtime <= ra_end_tai93+(ra_time_inc/2.):
                im_lon = np.abs(SATlon-ra_lon).argmin()
                im_lat = np.abs(SATlat-ra_lat).argmin()
                im_time = np.abs(SATtime-ra_tai93).argmin()
                
                for variable in variables:
                    if REALObsdata[variable].ndim == 3: # time, lat, lon
                        SSSdata[variable].ravel()[i] = REALObsdata[variable][im_time,im_lat,im_lon].data
                    else: # it's got an extra dimension (probably vertical)
                        SSSdata[variable].reshape(-1, SSSdata[variable].shape[-1])[i,:] = REALObsdata[variable][im_time,:,im_lat,im_lon].data
                        ###SSSdata[variable][i,:] = REALObsdata[variable][im_time,:,im_lat,im_lon] # this is what I had before
                        ###SSSdata[variable].ravel()[i] = merradataset[variable][im_time,im_lat,im_lon].flatten()[0]


        print('Finished Filling')
        
        # now just get the coordinates But I still have no way to trace back to this.  However, the vertical levels are useful.
        SSSdata[lonstring] = ra_lon
        SSSdata[latstring] = ra_lat
        SSSdata[timestring] = ra_time.data.copy()
        SSSdata['satlon'] = SATcoords['lon'].copy()
        SSSdata['satlat'] = SATcoords['lat'].copy()
        SSSdata['sattime'] = SATcoords['time'].copy()
        
        SSSdata['tai93'] = ra_tai93
        if 'ra_lev' in locals():
            SSSdata[levstring] = ra_lev


        if 'data' in locals(): # the close it
            data.close()

        if 'twoddata' in locals(): # the close it
            twoddata.close()

    if 'localfiles' in locals():
        for lfile in localfiles: # If I want to save the files I should remove this part.
            os.remove(lfile)



    return SSSdata











if __name__ == "__main__":

    '''
    This is just to test my simulation code
    '''

    '''
    In Jira ticket GUN-52 I identified the CLIMCAPS datasets to test with this.
 
Chris Barnet (2019), Sounder SIPS: JPSS-1 CrIS Level 2 CLIMCAPS: Atmosphere cloud and surface geophysical state V2, Greenbelt, MD, USA, Goddard Earth Sciences Data and Information Services Center (GES DISC), Accessed: [Data Access Date], 10.5067/LESQUBLWS18H

and

Global Modeling and Assimilation Office (GMAO) (2015), MERRA-2 inst3_3d_asm_Nv: 3d,3-Hourly,Instantaneous,Model-Level,Assimilation,Assimilated Meteorological Fields V5.12.4, Greenbelt, MD, USA, Goddard Earth Sciences Data and Information Services Center (GES DISC), Accessed: [Data Access Date], 10.5067/WWQSXQ8IVFW8
    '''
    

    

    
    begin_date = '2015.10.28T10:00:00Z'
    end_date = '2015.10.29T00:00:00Z'
    
    # Bounding box in the Gulf of Mexico
    lon=[-95.,-85.]
    lat=[20.,30.]


    datasetidsandvariables={}
    
    datasetidsandvariables['AIRS2SUP.7.0'] = ['Longitude','Latitude','Time','bndry_lyr_top','bndry_lyr_top_QC','GP_HeightSup','GP_HeightSup_QC','GP_Surface','GP_Surface_QC']

    datasetidsandvariables['AIRS2RET.7.0'] = ['Longitude','Latitude','Time','TSurfAir','TSurfAir_QC','TSurfStd','TSurfStd_QC','PSurfStd','PSurfStd_QC','solzen','nCld','CldFrcTot','CldFrcTot_QC','MWSurfClass','SurfClass','MWHingeSurfFreqGHz','EmisMWStd','EmisMWStd_QC','totH2OStd','totH2OStd_QC','GP_Height','GP_Height_QC','GP_Surface','GP_Surface_QC','RelHumSurf','RelHumSurf_QC','landFrac']

    datasetidsandvariables['AIRS2CCF.7.0'] = ['Longitude','Latitude','Time','scanang']
    
    ###datasetidsandvariables['AIRIBRAD.005'] = ['Longitude','Latitude','Time','scanang']

    aggdata = lagg(datasetidsandvariables,begin_date,end_date,lon=lon,lat=lat,reader='pyhdf',usemask=False)

    outstring = '_'.join(aggdata.keys())+'_'+begin_date+'_'+end_date

    myio.dict2h5(aggdata,'GulfofMexico'+outstring+'.h5')

    #tmpdata= h5py.File('ftpGreenlandSummit14years.h5','r')

    
    
    SATcoords = {'lon':aggdata['AIRS2RET.7.0']['Longitude'][:],'lat':aggdata['AIRS2RET.7.0']['Latitude'][:],'time':aggdata['AIRS2RET.7.0']['Time'][:]}


    ###MAT1NXSLV_variables = ['TS','T2M','T10M']
    ###MAT1NXSLVdata = sim_sat(SATcoords,'MAT1NXSLV.5.2.0',MAT1NXSLV_variables,reader='opendap')

    ###M2T3NVASM_variables = ['QV','RH','T']
    ###M2T3NVASMdata = sim_sat(SATcoords,'M2T3NVASM','5.12.4',M2T3NVASM_variables)


    M2T1NXSLV_variables = ['TS','T2M','T10M']
    M2T1NXSLVdata = sim_sat(SATcoords,'M2T1NXSLV','5.12.4',M2T1NXSLV_variables)


    M2T1NXFLX_variables = ['PBLH','TCZPBL']
    M2T1NXFLXdata = sim_sat(SATcoords,'M2T1NXFLX','5.12.4',M2T1NXFLX_variables)


    M2T3NVASM_variables = ['RH']
    M2T3NVASMdata = sim_sat(SATcoords,'M2T3NVASM','5.12.4',M2T3NVASM_variables)

    
    ###ERA5_variables = ['q','r','t','sp']
    ###ERA5data = sim_sat(SATcoords,'ERA','5',ERA5_variables,reader='netcdf4')

    simdata = {}
    simdata['M2T1NXSLV'] = M2T1NXSLVdata
    simdata['M2T1NXFLX'] = M2T1NXFLXdata
    simdata['M2T3NVASM'] = M2T3NVASMdata
    
    



    outstring = '_'.join(simdata.keys())+'_'+begin_date+'_'+end_date

    myio.dict2h5(simdata,'GulfofMexicoSSS'+outstring+'.h5')


    
