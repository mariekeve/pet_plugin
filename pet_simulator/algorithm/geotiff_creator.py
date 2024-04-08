from osgeo import gdal, osr, ogr  # Python bindings for GDAL
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

''' 
ds = gdal.open("in.tif")
dsReprj = gdal.Warp("out.tif", "in.tif", dstSRS = "EPSG:4326")
dsRes = gdal.Warp("out.tif", ds, xRes = 150, yRes = 150, resampleAlg = "bilinear")
dsClip = gdal.Warp("out.tif", "in.tif", cutlineDSName = "star.shp", cropToCutLine = True, dstNodata = np.nan)
array = dsClip.GetRasterBand(1).ReadAsArray()
plt.imshow(array)
'''

# --------------------------------------------------------------------------------------------------------------------------
def TifToArray(image):

    data = np.array(image)
    return data
# --------------------------------------------------------------------------------------------------------------------------
def GeotifToArray(image, nband):

    band = image.GetRasterBand(1)
    data = band.ReadAsArray()

    if nband > 1:
        data = np.ones((data.shape[0], data.shape[1], nband), dtype=np.uint8)
        for i in range(nband):
            band = image.GetRasterBand(i+1)
            dat = band.ReadAsArray()
            for j in range(data.shape[0]):
                for k in range(data.shape[1]):
                    data[j,k,i] = dat[j,k]

    geotransform = image.GetGeoTransform()
    xmin = geotransform[0]
    ymin = geotransform[3]
    cellsize = geotransform[1]
    nrow = data.shape[0]
    ncol = data.shape[1]

    ymin = geotransform[3] - nrow * cellsize # ???????????????

    metadata = [xmin, ymin, cellsize, nrow, ncol]

    return data, metadata

# --------------------------------------------------------------------------------------------------------------------------
def ArrayWrite(filename, data, metadata):

    with open(filename, 'at') as f:
        f.write(f'\n{metadata}\n\n')
        if len(data.shape) == 2:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    f.write(f'{data[i, j]:6.2f}')
                f.write('\n')
            f.write('\n')
        if len(data.shape) == 3:
            for k in range(data.shape[2]):
                for i in range(data.shape[0]):
                    for j in range(data.shape[1]):
                        f.write(f'{data[i, j, k]:6.2f}')
                    f.write('\n')
                f.write('\n')

# --------------------------------------------------------------------------------------------------------------------------
def ArrayWriteG(filename, name, inputfile):

    im = gdal.Open(inputfile)
    with open(filename, 'at') as f:
        f.write(f'\n{name}\n')
        data, metadata = GeotifToArray(im, 1)
        f.write(f'\n{metadata}\n\n')
        if len(data.shape) == 2:
            for ii in range(data.shape[0]):
                for jj in range(data.shape[1]):
                    f.write(f'{data[ii, jj]:6.2f}')
                f.write('\n')
            f.write('\n')
# --------------------------------------------------------------------------------------------------------------------------
def ArrayToTif(data):

    image = Image.fromarray(data)
    return image

"""
def GTifToJPG(self, basedirectory, subdirectory, filename):
    intiff = gdal.Open(f'{basedirectory}{subdirectory}\\{filename}')
    tifArray = intiff.ReadAsArray()
    image = Image.fromarray(tifArray)
    img = mpimg.imread(image)
    imgplot = plt.imshow(img)
    return imgplot
"""

# --------------------------------------------------------------------------------------------------------------------------
def TifToJPG(image):

    img = mpimg.imread(image)
    imgplot = plt.imshow(img)
    return imgplot

# --------------------------------------------------------------------------------------------------------------------------
def ArrayToGeotif(data, metadata):

    xmin = metadata[0]
    ymin = metadata[1]
    cellsize = metadata[2]
    nrow = metadata[3]
    ncol = metadata[4]

    # Get GDAL driver GeoTiff
    driver = gdal.GetDriverByName('GTiff')
    data_type = gdal.GDT_Float32

    # Create a temp grid
    # options = ['COMPRESS=JPEG', 'JPEG_QUALITY=80', 'TILED=YES']

    if len(data.shape) == 2:
        image = driver.Create('grid_data', xsize=ncol, ysize=nrow, bands=1, eType=data_type)  # , options)
        image.GetRasterBand(1).WriteArray(data)
    if len(data.shape) == 3:
        image = driver.Create('grid_data', xsize=ncol, ysize=nrow, bands=3, eType=data_type)  # , options)
        for k in range(data.shape[2]):
            image.GetRasterBand(k+1).WriteArray(data[:,:,k])

    # Spatial Reference System
    srs = osr.SpatialReference()
    #srs.ImportFromProj4('+proj=utm +ellps=EPSG28992 +datum=EPSG28992 +units=m')
    srs.ImportFromEPSG(28992)

    # Setup projection and geo-transform
    image.SetProjection(srs.ExportToWkt())
    ymax = ymin + cellsize * nrow
    trans = [xmin, cellsize, 0, ymax, 0, -cellsize]

    image.SetGeoTransform(trans)

    driver = None
    return image

# --------------------------------------------------------------------------------------------------------------------------

def GeotifWrite(file_name, image):

    driver = gdal.GetDriverByName('GTiff')
    print(f'Generated GeoTIFF: {file_name}')
    driver.CreateCopy(file_name, image, strict=0)

# --------------------------------------------------------------------------------------------------------------------------
def GeotifRead(filename):

    image = gdal.Open(filename)
    return image

# ======================================================================================================================
'''
stat = StatParameters(xmin=172075, xmax=172075+6, ymin=440675, ymax=440675+5, cellsize=1)
data = np.random.randint(0, 10, size=(stat.nrow, stat.ncol))
metadata = [stat.xmin, stat.ymin, stat.cellsize, stat.nrow, stat.ncol]

print(data)
print(metadata)

name = 'nootdorp'
geotif = ArrayToGeotif(data, metadata)
GeotifWrite(f'{name}.tif', geotif)

data, metadata = GeotifToArray(geotif)
ArrayWrite(f'{name}.txt', data, metadata)
'''