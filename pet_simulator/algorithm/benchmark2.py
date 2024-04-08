from geotiff_creator import ArrayToGeotif

from fraction_area_buildings_treeregr import FaBuildingTree
from pet_parameters import StatParameters, writer
from pet_parameters import DynParameters
from osgeo import gdal, osr, ogr

im = gdal.Open('D:/project/run2/sim12/input/run2sim12_building_height.tif') # large
stat = StatParameters(1,2,3,4)
dyn = DynParameters()
FaBuildingTree(stat, dyn, im, im, im, im)

