import pdb
import distutils.dir_util

# this program will get the latest version of the ECMWF reanalysis product.  ERA5.
import cdsapi
# The things to get are:         
#    'variable':'specific_humidity',
# or 'variable':'relative_humidity',
# or 'variable':'temperature',
import mytime


def get_ecmwf(begin_date,end_date,outdir='/home/thearty/data/ERA5/'):

    distutils.dir_util.mkpath(outdir) # this will create the output directory if it does not already exist.

    cds = cdsapi.Client()

    dtrange = mytime.datetime_range(begin_date,end_date)

    outfiles =[]

    for dt in dtrange:

        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        day = dt.strftime('%d')

        date_string = dt.strftime('%Y%m%d')

        print('###Getting ERA5 data for :'+date_string)

    # this gets the surface pressure for one day of one variable.

        

        outfile = outdir+'/SurfacePressure'+date_string+'.nc'
        outfiles.append(outfile)

        cds.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type':'reanalysis',
                'format':'netcdf',
                'variable':'surface_pressure',
                'year':year,
                'month':month,
                'day':day,
                'time':[
                    '00:00','01:00','02:00',
                    '03:00','04:00','05:00',
                    '06:00','07:00','08:00',
                    '09:00','10:00','11:00',
                    '12:00','13:00','14:00',
                    '15:00','16:00','17:00',
                    '18:00','19:00','20:00',
                    '21:00','22:00','23:00'
                   ]
               },
            outfile)

    # this gets the level quantities got specific humidity, relative humidity, and temperature


        outfile = outdir+'/TqRH'+date_string+'.nc'
        outfiles.append(outfile)

        cds.retrieve(
            'reanalysis-era5-pressure-levels',
            {
                'product_type':'reanalysis',
                'format':'netcdf',
                'variable':[
                    'relative_humidity','specific_humidity','temperature'
                   ],
                'pressure_level':[
                    '300','400','500',
                    '600','700','850',
                    '925','1000'
                   ],
                'year':year,
                'month':month,
                'day':day,
                'time':[
                    '00:00','01:00','02:00',
                    '03:00','04:00','05:00',
                    '06:00','07:00','08:00',
                    '09:00','10:00','11:00',
                    '12:00','13:00','14:00',
                    '15:00','16:00','17:00',
                    '18:00','19:00','20:00',
                    '21:00','22:00','23:00'
                   ]
               },
            outfile)

    return outfiles


if __name__ == "__main__":


    begin_date = '2004.09.11'
    end_date = '2004.10.01'
    outdir = '/home/thearty/data/ERA5'


    outfiles = get_ecmwf(begin_date,end_date,outdir=outdir)







