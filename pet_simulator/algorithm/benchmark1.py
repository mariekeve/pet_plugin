#ahn builder

import numpy as np
from PIL import Image
from osgeo import gdal, osr, ogr
from pet_parameters import directory_main
from pet_parameters import writer
from pet_parameters import StatParameters
from pet_parameters import DynParameters

from geotiff_creator import ArrayToGeotif   #(data, metadata):
from geotiff_creator import GeotifWrite     #(file_name, image):
from geotiff_creator import GeotifToArray #(image, bandnr=1)
from geotiff_creator import ArrayWrite #(filename, data, metadata)

dyn_parameters = DynParameters()
stat_parameters = StatParameters(xmin=172076-4, xmax=172080+4, ymin=440676-4, ymax=440680+4, cellsize=1,
        station='herwijnen', station_lat=51.859, station_lon=5.146)
metadata = [stat_parameters.xmin, stat_parameters.ymin, stat_parameters.cellsize, stat_parameters.nrow, stat_parameters.ncol]
print(metadata)
sizex = stat_parameters.ncol
sizey = stat_parameters.nrow

def plotr(arr):
    min = arr.min()
    max = arr.max()
    for i in range(len(arr)):
        arr[i] = (arr[i] - min) * 255 / (max - min)
    print(arr)
    im = Image.fromarray(arr)
    im.show()

def saver(arr, filename):
    im = Image.fromarray(arr)
    im.save(filename)

def saverG(filename, arr, metadata):
    im = ArrayToGeotif(arr, metadata)
    GeotifWrite(filename, im)

def writerG(filename, name, image, nband):
    with open(filename, 'at') as f:
        f.write(f'\n{name}\n')
    data, metadata = GeotifToArray(image, nband)
    ArrayWrite(filename, data, metadata)

f = open(f'{directory_main}text/rawrun1.txt', 'wt')
f.close()
f = open(f'{directory_main}text/raw.txt', 'wt')
f.close()

#-----------------------------------------------------------------------------------------------------------------------
# terreinhoogte incl gebouwen, bomen (DSM)
# read pointcloud from ahn4 viewer website translate to raster in QGIS
# todo automated in plugin

ahn = np.ones((sizey,sizex))
ahn = ahn * 0.1

# building
ahn[1,1] = 5
ahn[1,2] = 3
ahn[2,1] = 4
ahn[2,2] = 4

ahn[3,5] = 5
ahn[3,6] = 5
ahn[4,5] = 5
ahn[4,6] = 5

# tree
ahn[2,3] = 3
#ahn[3,5] = 3

# grass
ahn[3,0] = 0.2
ahn[3,1] = 0.2
ahn[3,2] = 0.2

# water
ahn[4,3] = 0
ahn[4,4] = 0
ahn[3,4] = 0

ahn[5,7] = 5
ahn[5,8] = 5
ahn[6,7] = 5
ahn[6,8] = 5

#plotr(ahn)
im = ArrayToGeotif(ahn, metadata)
GeotifWrite(f'{directory_main}data/ahn.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/ahn.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
# gebouwen mask raster
# raterized building polygons from geofbriek.de

building_mask = np.zeros((sizey,sizex), dtype=int)

building_mask[5,7] = 1
building_mask[5,8] = 1
building_mask[6,7] = 1
building_mask[6,8] = 1

im = ArrayToGeotif(building_mask, metadata)
GeotifWrite(f'{directory_main}data/building_mask.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/building_mask.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
# gemiddelde gebouwhoogte
# filter ahn with building mask
# todo generalize for more than one building

building = np.zeros((sizey,sizex))

height = 0
count = 0
for i in range(sizey):
    for j in range(sizex):
        if building_mask[i,j] == 1:
            height += ahn[i,j]
            count += 1

if count > 0:
    meanheight = height / count
    if meanheight > 2:
        for i in range(sizey):
            for j in range(sizex):
                if building_mask[i, j] == 1:
                    building[i, j] = meanheight

im = ArrayToGeotif(building, metadata)
GeotifWrite(f'{directory_main}data/building_height.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/building_height.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
# bomen mask raster
# from bomenregister
# todo polygon naar raster

tree_mask = np.zeros((sizey,sizex), dtype=int)
#tree_mask[2,3] = 1
#tree_mask[3,5] = 1

im = ArrayToGeotif(tree_mask, metadata)
GeotifWrite(f'{directory_main}data/tree_mask.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/tree_mask.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
# tree height from ahn
# todo more than one tree

tree = np.zeros((sizey,sizex))

height = 0
count = 0
for i in range(sizey):
    for j in range(sizex):
        if tree_mask[i,j] == 1:
            height += ahn[i,j]
            count += 1
if count > 0:
    meanheight = height / count
    if meanheight > 2:
        for i in range(sizey):
            for j in range(sizex):
                if tree_mask[i, j] == 1:
                    tree[i, j] = meanheight

im = ArrayToGeotif(tree, metadata)
GeotifWrite(f'{directory_main}data/tree_height.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/tree_height.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
# water mask
# water from geofabrik.de landuse

water_mask = np.zeros((sizey,sizex), dtype=int)

# water
water_mask[4,3] = 1
water_mask[4,4] = 1
water_mask[3,4] = 1

#plotr(ahn)
im = ArrayToGeotif(water_mask, metadata)
GeotifWrite(f'{directory_main}data/water_mask.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/water_mask.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
# sky view factor
# raster from knmi data 1 m resolution

svf = np.zeros((sizey,sizex))

svf[0,0] = 0.5
svf[0,1] = 0.5
svf[0,2] = 0.5
svf[0,3] = 1
svf[0,4] = 1
svf[0,5] = 1
svf[1,0] = 0.5
svf[1,3] = 1
svf[1,4] = 1
svf[1,5] = 1
svf[2,0] = 0.5
svf[2,4] = 1
svf[2,5] = 1

#building
svf[1,1] = 1
svf[1,2] = 0.5
svf[2,1] = 1
svf[2,2] = 1

#water
svf[4,3] = 0.5
svf[4,4] = 1
svf[3,4] = 1

im = ArrayToGeotif(svf, metadata)
GeotifWrite(f'{directory_main}data/svf.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/svf.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
#sky view factor zonder gebouw en water
# from svf and buildings mask en water mask

svf_mask = np.zeros((sizey,sizex))

for i in range(sizey):
    for j in range(sizex):
        if building_mask[i,j] == 0 and water_mask[i,j] == 0:
            svf_mask[i,j] = 1

im = ArrayToGeotif(svf_mask, metadata)
GeotifWrite(f'{directory_main}data/svf_mask.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/svf_mask.tif', im, 1)

#-----------------------------------------------------------------------------------------------------------------------
# rater red green blue
# from pdok

rgb = np.ones((sizey,sizex,3), dtype=np.uint8)

for i in range(3):

    # tree
    rgb[2,3,i] = 50+i
    rgb[3,5,i] = 50+i

    # grass
    rgb[3,0,i] = 50+i
    rgb[3,1,i] = 50+i
    rgb[3,2,i] = 50+i

im = ArrayToGeotif(rgb, metadata)
GeotifWrite(f'{directory_main}data/ndvi_rgb.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/ndvi_rgb.tif', im, 3)

#-----------------------------------------------------------------------------------------------------------------------
# rater infrared
# from pdok

inf = np.ones((sizey,sizex,3), dtype=np.uint8)

for i in range(3):

    # tree
    inf[2,3,i] = 100
    inf[3,5,i] = 100

    # grass
    inf[3,0,i] = 100
    inf[3,1,i] = 100
    inf[3,2,i] = 100

im = ArrayToGeotif(inf, metadata)
GeotifWrite(f'{directory_main}data/ndvi_infr.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}input/ndvi_infr.tif', im, 3)

#-----------------------------------------------------------------------------------------------------------------------
# shadow
# Shadow_20220621_0945_LST.tif from umep gis tool

lst = np.zeros((sizey,sizex))

year = dyn_parameters.year
month = dyn_parameters.month
day = dyn_parameters.day
hour = dyn_parameters.hour
min = dyn_parameters.min

filenameshadow = f'Shadow_{year}{month:02d}{day:02d}_{hour:02d}{min:02d}_LST'

# pavement
lst[0,0] = 1
lst[0,1] = 1
lst[0,2] = 1
lst[1,0] = 1
lst[2,0] = 1

lst[0,3] = 0
lst[0,4] = 0
lst[0,5] = 0
lst[1,3] = 0
lst[1,4] = 0
lst[1,5] = 0
lst[2,4] = 0
lst[2,5] = 0

im = ArrayToGeotif(lst, metadata)
GeotifWrite(f'{directory_main}/data/{filenameshadow}.tif', im)
writerG(f'{directory_main}text/raw.txt', f'{directory_main}/input/{filenameshadow}.tif', im, 1)

#im = Image.open('c:/tmp/Shadow_20230520_0700_LST.tif')
#svf = np.array(im)
#with np.printoptions(threshold=np.inf):
#    print(svf)

#S_svf = svf[2,2]
#PET_shadenight  = -12.14 + 1.25 T_a - 1.47 np.log (u_12 + 0.060 T_w + 0.015 S_vf Q_d + 0.0060(1 - S_vf) sigma (T_a + 273.14)**4