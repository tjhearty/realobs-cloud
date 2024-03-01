import pdb

# this program will get the latest version of the ECMWF reanalysis product.  ERA5.
import cdsapi
# The things to get are:         
#    'variable':'specific_humidity',
# or 'variable':'relative_humidity',
# or 'variable':'temperature',
import mytime


def get_monthlyecmwf(begin_date,end_date,outdir='/tmp/'):


    cds = cdsapi.Client()

    alldays = mytime.datetime_range(begin_date,end_date)

    allmonths = []
    for day in alldays:
        if day.day == 1:
            allmonths.append(day)


    outfiles =[]

    for dt in allmonths:

        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        day = dt.strftime('%d')

        date_string = dt.strftime('%Y%m%d')

        print '###Getting ERA5 data for :'+date_string 

    # this gets the level quantities got specific humidity, relative humidity, and temperature

        outfile = outdir+'/Monthly1x1TqRH'+date_string+'.nc'
        outfiles.append(outfile)

        year = dt.strftime("%Y")
        month = dt.strftime("%m")

        cds.retrieve(
            'reanalysis-era5-pressure-levels-monthly-means',
            {
            'grid': '1.0/1.0',
            'format':'netcdf',
            'product_type':'monthly_averaged_reanalysis',
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
            'time':'00:00'
               },
            outfile)

    return outfiles


if __name__ == "__main__":


    begin_date = '2002.09.01'
    end_date = '2016.09.30'
    outdir = '/home/thearty/data/ERA5'


    outfiles = get_monthlyecmwf(begin_date,end_date,outdir=outdir)







