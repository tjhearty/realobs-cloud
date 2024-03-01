from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *


import geoutils
import tai93

from astropy.time import Time 

###airsfile = 'AIRS.2017.01.10.001.L2.RetStd_IR.v6.0.31.0.G17010151737.hdf'
airsfile = '/home/thearty/tmp/AIRS.2012.02.29.240.L2.CO2_Std.v5.4.11.0.CO2.T12076224746.hdf'

hdfvars = SD(airsfile, SDC.READ)
airs_Time = hdfvars.select('Time')[:]

tai93.tai93_to_utc(airs_Time[0,0])



t_utc19930101 = Time('1993-01-01')
t_gps19930101 = t_utc19930101.gps # this converts the time to GPS

t_gps = Time(t_gps19930101 + airs_Time[0,0], scale='tai', format='gps')
