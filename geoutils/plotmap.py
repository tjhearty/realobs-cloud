import numpy as np
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt

def plotmap(lons,lats,data_in,vmin=None,vmax=None,fillvalue=-9999.0):
    """
    Plot a 2-D data array given a longitude and latitude.
    """
    validdata = data_in != fillvalue
    if vmax == None:
        vmax = data_in[validdata].max()
    if vmin == None:
        vmin = data_in[validdata].min()
        
    data = np.clip(data_in,vmin,vmax)
    ###fig = plt.figure(figsize=(8,8))
    ###ax = fig.add_axes([0.1,0.1,0.8,0.8])
    # create Basemap instance.
    m = Basemap(projection='cyl')
    # draw parallels.
    parallels = np.arange(-90.,90,30.)
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
    # draw meridians
    meridians = np.arange(0.,360.,30.)
    m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)
    m.drawcoastlines()
    im1 = m.pcolormesh(lons,lats,data,shading='flat',cmap=plt.cm.jet,latlon=True,vmin=vmin,vmax=vmax)
    cbar = m.colorbar(im1,location='bottom',pad="7%")
    cbar.set_label('K')
    plt.show()
    #plt.show(block=False)
