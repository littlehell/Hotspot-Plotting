1.required python extension packages:
 GDAL for python or osgeo
 georaster
 matplotlib
 mpltoolkits.basemap
 pyhdf
 
 to install these packages, search from https://www.lfd.uci.edu/~gohlke/pythonlibs/ or download from official site
 to install georaster package, use "pip install georaster"
 while installing packages, maybe other dependent libraries required, check errors during installation

2.usage
 "python plotting.py <absolute path of geotiff> <absolute path of HDF>" for use
 "python plotting.py -h" for help
 "python plotting.py <absolute path of geotiff> <absolute path of HDF> -l" to add individual hotspot count location

3.env
 development environment:Windows 7 with Python 3.5
 should be used on Linux with Python 3