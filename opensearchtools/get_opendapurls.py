import geoutils
import urllib2
import re

def get_opendapurls(dataset,begin_date,end_date,lon=None,lat=None,rad_km=None):
    """
       Return a list of opendap urls given the above input parameters.  It will convert the radius to bounding box centered on the given longitude and latitude

       This is an early version that used re to search for the opendap string.  get_MOSurls.py actually parses the xml which I think is better.
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
        bb = geoutils.r2bb(lon,lat,rad_km) # bounding box tuple
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
