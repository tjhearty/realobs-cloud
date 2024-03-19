import numpy as np
import h5py
import pdb





def dict2h5(indict,outfile,fill_value=-9999.,lon_string=None,lat_string=None,time_string=None):
    """
    Write a dictionary to an h5 file.

    dict2h5(indict,outfile)

    Here are some other things I can do but I don't need them.

    grp = f.create_group(saggdata.keys()[0])
    dset2 = grp.create_dataset("another_dataset", (50,), dtype='f')


    dset = f.create_dataset('subgroup2/dataset_three', (10,), dtype='i')
    dset.attrs['temperature'] = 99.5
    """

    coordinate_variables = ['lat_l3','lon_l3','plev','lat_Obs4MIPs','lon_Obs4MIPs','lon','lat','satlon','satlat','time']
    if type(lon_string) == str:
        coordinate_variables.append(lon_string)
    if type(lon_string) == str:
        coordinate_variables.append(lat_string)
    if type(lon_string) == str:
        coordinate_variables.append(time_string)    

    

    # write the data to a file

    f = h5py.File(outfile, "w")

    for key in indict.keys():

        if key in coordinate_variables:

            dset = f.create_dataset(key, data=indict[key])

            if key == 'lat_l3':
                dset.attrs['units'] = 'degrees_north'
                dset.attrs['standard_name'] = 'latitude'
                dset.attrs['long_name'] = 'latitude'
                dset.attrs['axis'] = 'lat_l3'

            if key == 'lon_l3':
                dset.attrs['units'] = 'degrees_east'
                dset.attrs['standard_name'] = 'longitude'
                dset.attrs['long_name'] = 'longitude'
                dset.attrs['axis'] = 'lon_l3'

            if key == 'plev':
                dset.attrs['units'] = 'Pa'
                dset.attrs['standard_name'] = 'air_pressure'
                dset.attrs['long_name'] = 'pressure'
                dset.attrs['axis'] = 'Z'
                dset.attrs['positive'] = 'down'

            if key == 'lat_Obs4MIPs':
                dset.attrs['units'] = 'degrees_north'
                dset.attrs['standard_name'] = 'latitude'
                dset.attrs['long_name'] = 'latitude'
                dset.attrs['axis'] = 'lat_Obs4MIPs'

            if key == 'lon_Obs4MIPs':
                dset.attrs['units'] = 'degrees_east'
                dset.attrs['standard_name'] = 'longitude'
                dset.attrs['long_name'] = 'longitude'
                dset.attrs['axis'] = 'lon_Obs4MIPs'

            if key == 'lat':
                dset.attrs['units'] = 'degrees_north'
                dset.attrs['standard_name'] = 'latitude'
                dset.attrs['long_name'] = 'latitude'
                dset.attrs['axis'] = 'Y'

            if key == 'lon':
                dset.attrs['units'] = 'degrees_east'
                dset.attrs['standard_name'] = 'longitude'
                dset.attrs['long_name'] = 'longitude'
                dset.attrs['axis'] = 'X'

            if key == 'satlat':
                dset.attrs['units'] = 'degrees_north'
                dset.attrs['standard_name'] = 'latitude'
                dset.attrs['long_name'] = 'latitude'
                dset.attrs['axis'] = 'Y'

            if key == 'satlon':
                dset.attrs['units'] = 'degrees_east'
                dset.attrs['standard_name'] = 'longitude'
                dset.attrs['long_name'] = 'longitude'
                dset.attrs['axis'] = 'X'
                
            if key == 'time':
                dset.attrs['units'] = 'seconds since 1993-01-01' # fix this later
                dset.attrs['standard_name'] = 'time'
                dset.attrs['long_name'] = 'time'
                dset.attrs['axis'] = 'T'
                

    for key in indict.keys():
        print(key)

        if isinstance(indict[key],dict): # this means it is a dictionary and thus has groups
    
            for variable in indict[key].keys():
                print(variable)

                if 'Obs4MIPs' in key:

                    fillvalue=1.0e20
 
                else:

                    fillvalue=fill_value

                if type(indict[key][variable]) == 'S32': # this is for the scan_node_type
            
                    fillvalue=None

                if key not in coordinate_variables:
                    
                    dset = f.create_dataset(key+'/'+variable, data=indict[key][variable],fillvalue=fillvalue)

                else:

                    pdb.set_trace()
                    dset = f.create_dataset(key+'/'+variable, data=indict[key])

                    if key == 'lat_l3':
                        dset.attrs['units'] = 'degrees_north'
                        dset.attrs['standard_name'] = 'latitude'
                        dset.attrs['long_name'] = 'latitude'
                        dset.attrs['axis'] = 'lat_l3'

                    if key == 'lon_l3':
                        dset.attrs['units'] = 'degrees_east'
                        dset.attrs['standard_name'] = 'longitude'
                        dset.attrs['long_name'] = 'longitude'
                        dset.attrs['axis'] = 'lon_l3'

                    if key == 'plev':
                        dset.attrs['units'] = 'Pa'
                        dset.attrs['standard_name'] = 'air_pressure'
                        dset.attrs['long_name'] = 'pressure'
                        dset.attrs['axis'] = 'Z'
                        dset.attrs['positive'] = 'down'

                    if key == 'lat_Obs4MIPs':
                        dset.attrs['units'] = 'degrees_north'
                        dset.attrs['standard_name'] = 'latitude'
                        dset.attrs['long_name'] = 'latitude'
                        dset.attrs['axis'] = 'lat_Obs4MIPs'

                    if key == 'lon_Obs4MIPs':
                        dset.attrs['units'] = 'degrees_east'
                        dset.attrs['standard_name'] = 'longitude'
                        dset.attrs['long_name'] = 'longitude'
                        dset.attrs['axis'] = 'lon_Obs4MIPs'

                    if key == 'lat':
                        dset.attrs['units'] = 'degrees_north'
                        dset.attrs['standard_name'] = 'latitude'
                        dset.attrs['long_name'] = 'latitude'
                        dset.attrs['axis'] = 'Y'
  
                    if key == 'lon':
                        dset.attrs['units'] = 'degrees_east'
                        dset.attrs['standard_name'] = 'longitude'
                        dset.attrs['long_name'] = 'longitude'
                        dset.attrs['axis'] = 'X'

                    if key == 'satlat':
                        dset.attrs['units'] = 'degrees_north'
                        dset.attrs['standard_name'] = 'latitude'
                        dset.attrs['long_name'] = 'latitude'
                        dset.attrs['axis'] = 'Y'

                    if key == 'satlon':
                        dset.attrs['units'] = 'degrees_east'
                        dset.attrs['standard_name'] = 'longitude'
                        dset.attrs['long_name'] = 'longitude'
                        dset.attrs['axis'] = 'X'
                
                    if key == 'time':
                        dset.attrs['units'] = 'days since 2000-01-01'
                        dset.attrs['standard_name'] = 'time'
                        dset.attrs['long_name'] = 'time'
                        dset.attrs['axis'] = 'T'

                    if key == lon_string:
                        dset.attrs['units'] = 'degrees_east'
                        dset.attrs['standard_name'] = 'longitude'
                        dset.attrs['long_name'] = 'longitude'

                    if key == lat_string:
                        dset.attrs['units'] = 'degrees_north'
                        dset.attrs['standard_name'] = 'latitude'
                        dset.attrs['long_name'] = 'latitude'

                    if key == time_string:
                        dset.attrs['units'] = 'seconds since 1993-01-01'
                        dset.attrs['standard_name'] = 'time'
                        dset.attrs['long_name'] = 'time'

                        

        else: # it doesn't have groups

            if key not in coordinate_variables:

                if 'Obs4MIPs' in key:

                    fillvalue=1.0e20
        
                else:

                    fillvalue=fill_value

                dset = f.create_dataset(key, data=indict[key],fillvalue=fillvalue)

                '''
                if f[key].ndim == 2:
                    
                    if 'grid' in key:

                        f[key].dims[0].label = 'lat'
                        f[key].dims[1].label = 'lon'
                    
                        # lets see if this works
                        f[key].dims[0].attach_scale(f['lat'])
                        f[key].dims[1].attach_scale(f['lon'])

                    else:
                        pdb.set_trace()
                '''


                if f[key].ndim == 3:

                    if 'Obs4MIPs' in key:
              
                        f[key].dims[0].label = 'plev'
                        f[key].dims[1].label = 'lat_Obs4MIPs'
                        f[key].dims[2].label = 'lon_Obs4MIPs'

                    else:

                        f[key].dims[0].label = 'lon_l3'
                        f[key].dims[1].label = 'lat_l3'
                        f[key].dims[2].label = 'plev'                


                if f[key].ndim == 4:

                    f[key].dims[0].label = 'time'
                    f[key].dims[1].label = 'plev'
                    f[key].dims[2].label = 'lat'
                    f[key].dims[3].label = 'lon'
                    
                    # lets see if this works
                    f[key].dims[0].attach_scale(f['time'])
                    f[key].dims[1].attach_scale(f['plev'])
                    f[key].dims[2].attach_scale(f['lat'])
                    f[key].dims[3].attach_scale(f['lon'])

    f.close()
    


