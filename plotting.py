# -*- coding: utf-8 -*-
#
# for plotting hotspots on satellite truecolor/RGB/IR product
#
#

from osgeo import gdal
import georaster
from pyhdf.SD import SD
import matplotlib.pyplot as plt
import matplotlib.image as mpi
from mpl_toolkits.basemap import Basemap
import countries
import pyhdf.error
import sys
from optparse import OptionParser


def readband(tiffile):
    # read bands of tiff file
    dataset = gdal.Open(tiffile)

    return dataset.RasterCount


def loadtiff(tiffile):
    # path of geotiff file

    # read extent of image without loading
    # get geo-referencing without loading image
    my_image = georaster.MultiBandRaster(tiffile, load_data=False)

    # grab limits of image's extent
    minx, maxx, miny, maxy = my_image.extent

    # return the geo-range of satellite product
    return minx, maxx, miny, maxy


def loadhdf(hdffile):
    # load hdf file
    hdff = SD(hdffile)

    # get latitude and longitude of hotspots
    # format of data is list
    lat_obj = hdff.select('FP_latitude')
    latdata = lat_obj.get()

    lon_obj = hdff.select('FP_longitude')
    londata = lon_obj.get()

    return latdata, londata


def nationjudge(hdffile):
    # according to the latitude and longitude given by hotspot HDF file
    # judge which country the coordinates are located in
    cc = countries.CountryChecker('TM_WORLD_BORDERS-0.3.shp')
    lat, lon = loadhdf(hdffile)
    country = []
    for i in range(lat.__len__()):
        c = cc.getCountry(countries.Point(float(lat[i]), float(lon[i])))
        country.append(str(c))

    return country


def imageplotting(tiffile, hdffile, hotspotloc=False):
    print('Plotting hotspots image')
    lonmin, lonmax, latmin, latmax = loadtiff(tiffile)

    # select the resolution of image, figsize=(hundred pixels×hundred pixels)
    plt.figure(figsize=(24, 24))

    # add basemap, select range of latitude and longitude
    # llcrnrlon: longitude of lower left hand corner of the desired map domain (degrees)
    # llcrnrlat: latitude of lower left hand corner of the desired map domain (degrees)
    # urcrnrlon: longitude of upper right hand corner of the desired map domain (degrees)
    # urcrnrlat: latitude of upper right hand corner of the desired map domain (degrees)
    # select resolution, could be c (crude), l (low), i (intermediate), h (high), f (full) or None. If None, no
    # boundary data will be read in
    map = Basemap(llcrnrlat=latmin, urcrnrlat=latmax, llcrnrlon=lonmin, urcrnrlon=lonmax, resolution='h')

    # read an image from the geotiff file into an array
    # return value is numpy.array
    img = mpi.imread(tiffile)

    bands = readband(tiffile)

    if bands > 1:
        """
        if here's image with multi bands, extent and origin keywords set automatically so image will be drawn over
        map region
        """
        print('Plotting truecolor/RGB image')
        # select 'zorder' to 1, set the image on the lowest floor
        map.imshow(img[::-1], zorder=1)
    elif bands == 1:
        # if here's image with single band, basecolor is purple
        # set colormap to 'gist_gray' and get the grayscale image
        print('Plotting IR image')
        map.imshow(img[::-1], zorder=1, cmap=plt.get_cmap('gist_gray'))

    lat, lon = loadhdf(hdffile)

    # plot scatter points of hotspot
    # parameter c controls color of points
    """
    marker controls shape of points, it can be either an instance of the class or the text shorthand for a particular 
    marker
    """
    map.scatter(lon, lat, c='r', marker='.', zorder=2)

    # draw coastlines
    # to change resolution, change 'resolution' selected in Basemap
    map.drawcoastlines()

    country = nationjudge(hdffile)
    # for hotspotloc == true, individual hotspot count location would be added
    if hotspotloc == True:
        hotspotcoors = []
        for i in range(lat.__len__()):
            hotspotcoors.append([float('%.2f' % lat[i]), float('%.2f' % lon[i]), country[i]])

        # add col labels
        col_labels = ['latitude', 'longitude', 'country']
        # add coordinates and countries into table
        plt.table(cellText=hotspotcoors, colWidths=[0.07] * 3, rowLabels=None, colLabels=col_labels, loc=4, zorder=3)

    # add up the number of hotsopts in each country and draw the table
    nations = set(country)
    nationname = []
    nationnumber = []
    for nation in nations:
        nationname.append(nation)
        nationnumber.append([country.count(nation)])

    plt.table(cellText=nationnumber, colWidths=[0.07], rowLabels=nationname, colLabels=['number'], loc=1, zorder=3)

    # plt.show()
    # save the image
    savename = tiffile.split('.tif')
    plt.savefig('{0}-{1}.png'.format(savename[0], 'hotspot'))


if __name__ == '__main__':
    # add help info for the program, type -h or --help to show
    usage = "**************************************\n" \
            "       ** <program>.exe GeoTiffile HDFfile **\n" \
            "       **************************************"
    parse = OptionParser(usage)

    # to add individual hotspot count location, add -l or --hotspotloc
    # image without hotspot locations is default
    parse.add_option('-l', '--hotspotloc', action='store_true', dest='location', default=False,
                     help='add individual hotspot count location')

    (option, arges) = parse.parse_args()

    # keep parameters of filename, so the position of '-l' is slight
    try:
        for i in sys.argv:
            if i.startswith('-'):
                sys.argv.remove(i)

        # position of the two filenames should not be reversed
        tiffile = sys.argv[1]
        hdffile = sys.argv[2]

        if option.location == True:
            imageplotting(tiffile, hdffile, hotspotloc=True)
        else:
            imageplotting(tiffile, hdffile)
    except IndexError:
        # for typing wrong number of files, return IndexError
        print('bad parameter, type "-h" or "--help" for help')
    except FileNotFoundError:
        # for the file is nonexistent, return FileNotFoundError
        print('no such files or wrong file, check again')
    except RuntimeError:
        # if the geotiff file is unreadable or broken, return RuntimeError
        print('no such files or wrong file, check again')
    except pyhdf.error.HDF4Error:
        # if the HDF file is unreadable or broken, return pyhdf.error.HDF4Error
        print('bad HDF file, check again')
    except AttributeError:
        # if array of geotiff data is bad or band number is wrong, return AttributeError
        print('bad GeoTiff file, check again')

