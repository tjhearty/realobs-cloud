import geoutils
import urllib2
from lxml import etree
import time
import datetime


def xml2urls(xml_str,urltype):
    """
    This program takes an xml string and just returns the "opendap" or "data" urls
    """

    # parse the xml
    xml = etree.fromstring(xml_str)

    # This XML has namespace.
    namespace = {"atom": "http://www.w3.org/2005/Atom"}

    # This xpath will find all the link nodes whoe 'rel' attribute is http://esipfed.org/ns/fedsearch/1.0/opendap#
    xpath = '//atom:link[@rel="http://esipfed.org/ns/fedsearch/1.0/%s#"]' % urltype

    # run the xpath
    results = xml.xpath(xpath, namespaces=namespace)


    # get the href attribute values out
    urls = [element.get('href') for element in results]

    # the opendap urls end in .html which I don't want.
    for i,url in enumerate(urls):
        newurl = url.replace('.html','')
        urls[i] = newurl

    urls = list(set(urls)) # makes them unique and sorts them

    urls.sort() # this will probably put them in chronological order but it must be verified.

    return urls




def get_MOSurls(dataset,start_time,end_time,lon=None,lat=None,rad_km=None,urltype='data',xml=None):
    """
       The program gets a list of Mirador OpenSearch (MOS) urls either.   The returned url type is either data or opendap.
INPUTS
    "dataset" the data set shortname

    "start_time"  start time in utc.  The following is appended to the date: "T00:00:00Z.

    "end_time"  start time in utc The following is appended to the date: "T00:00:00Z, thus the end date is not actualy included in the results.

    "lon", "lat", "rad_km" (optional) will search withing a given radius near a given location The input radius is converted to a bounding box.  If a radius is not given, it will find all of the granules on

    "urltype" Can be either "data" (default) or "opendap".

OUTPUTS

    "urls" A list of urls that match the search criteria
     
EXAMPLE

    Find all of the AIRX2RET granules within 30 km of  New Orleans

    > from opensearchtools.get_MOSurls import get_MOSurls
    > urls = get_MOSurls('AIRX2RET.006','2002.09.01','2016.01.01',lon=-90.0667,lat=29.95, rad_km=30.0)

    If a radius is not specified it will return all of the granules on the days in the search period.  For     example, following will return 241 granules.  The 1 extra if from 2002.08.31 part of which is on 2002.09.01

    > 
    > urls = get_MOSurls('AIRX2RET.006','2002.09.01','2002.09.02')

HISTORY

    Created by Thomas Hearty,  March 14, 2016 

NOTES
     
Return a list of data set urls given the above input parameters.  It will convert the radius to bounding box centered on the given longitude and latitude

I will follow Christines instructions for this.  She gave an example using opendap but I will make it work for the data urls instead and later convert the data urls to opendap urls.  The OPeNDAP urls are not in the OpenSearch results because doing so breaks the MERRA subsetter.  Probably because it doesn't know how to do this.

Here is Christine's sample code

from lxml import etree
import urllib2

# download the search output
xml_str = urllib2.urlopen("http://mirador.gsfc.nasa.gov/cgi-bin/mirador/granlist.pl?searchType=Nominal&format=atom&startTime=2002-09-01T00:00:00Z&endTime=2002-09-30T00:00:00Z&osLocation=-39.377320,72.311218,-37.574658,72.844513&maxgranules=100&dataSet=AIRX2RET.006",).read()

# parse the xml
xml = etree.fromstring(xml_str)

# This XML has namespaces.
namespaces = {"atom": "http://www.w3.org/2005/Atom"}

# This xpath will find all the link nodes whoe 'rel' attribute is http://esipfed.org/ns/fedsearch/1.0/opendap#
xpath = '//atom:link[@rel="http://esipfed.org/ns/fedsearch/1.0/opendap#"]'

# run the xpath
results = xml.xpath(xpath, namespaces=namespaces)

# get the href attribute values out
links = [element.get('href') for element in results]

# print them out
for link in links:
    print link

    """



    start_time = start_time.replace('.','-')
    end_time = end_time.replace('.','-')

    if len(start_time) == 10:
        start_time = start_time+"T00:00:00Z"
        end_time = end_time+"T00:00:00Z"



    # create a list of start and end times strings
    start_dt = datetime.datetime.fromtimestamp(time.mktime(time.strptime(start_time,"%Y-%m-%dT%H:%M:%SZ")))
    end_dt = datetime.datetime.fromtimestamp(time.mktime(time.strptime(end_time,"%Y-%m-%dT%H:%M:%SZ")))

    deltatime = end_dt - start_dt

    start_times = [start_time]
    end_times = []

    timeincrement = datetime.timedelta(7)

    while deltatime > timeincrement:
        old_start_dt = start_dt
        start_dt = old_start_dt+timeincrement
        end_times.append(start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
        start_times.append(end_times[-1])
        deltatime = end_dt - start_dt
    end_times.append(end_time)


    # create the bounding box string
    if rad_km is None: # A point search is not possible at this time.
        bb_string=''
    else:
        bb = geoutils.r2bb(lon,lat,rad_km) # bounding box tuple
        bb_string = "osLocation="+str(bb[0])+','+str(bb[1])+','+str(bb[2])+','+str(bb[3])+"&"


    urls = []

    for start_time_seg,end_time_seg in zip(start_times,end_times):

        date_string = "startTime="+start_time_seg+"&endTime="+end_time_seg+"&"  

        print date_string # comment out later.  This is just so I know how fast it is working.

        opensearch_string = "http://mirador.gsfc.nasa.gov/cgi-bin/mirador/granlist.pl?" \
        "searchType=Nominal&format=atom&" \
        +date_string+bb_string+"maxgranules=5000000&dataSet="+dataset


        xml_str = urllib2.urlopen(opensearch_string).read()

        urls_seg = xml2urls(xml_str,urltype)

        if len(urls_seg) > 0:
            urls.extend(urls_seg)

    # we did this already, but lest do it again because the same file can appear in multiple segments.
    urls = list(set(urls)) # makes them unique and sorts them



    urls.sort() # this will probably put them in chronological order but it must be verified.

    return urls,xml_str


if __name__ == "__main__":

    '''
    This is just some code to test get_MOSurls.py.
http://airsl2.gesdisc.eosdis.nasa.gov/data/Aqua_AIRS_Level2/AIRX2RET.006/2002/249/AIRS.2002.09.06.240.L2.RetStd.v6.0.7.0.G13202075916.hdf
    '''

    urls,xml_str = get_MOSurls('AIRX2RET.006','2002.09.06','2002.09.07')

    outfile = 'MOSlist.txt'
    output = open(outfile,'w')

    for url in urls:
        output.write(url+'\n')
    output.close()

    xmlfile = 'MOS.xml'
    output = open(xmlfile,'w')
    for line in xml_str:
        output.write(line)
    output.close()
