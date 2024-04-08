# PET simulator

PET simulator is an public accessible ui application in python installed for QGIS for indicating 1m resolution heat stress in the Netherlands. The code is based on the code of Koopmans et al. (2020) "A standardized Physical Equivalent Temperature urban heat map at 1-m spatial resolution to facilitate climate stress tests in the Netherlands".

## Installation

Download the PET_simulator as zip file and instalise at the place of the QGIS python plugins.
Example:
C:\Users\[...]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\pet_simulator

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
# Bindings PyQt for Qt designer 
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication #Qdate
from qgis.core import QgsRasterLayer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsRectangle
from osgeo import gdal, osr, ogr #Python bindings for GDAL
from .resources import *
import os.path
#calculating algorithms
import numpy as np
import pandas as pd
import multiprocessing as mp
import datetime
import time
import matplotlib.pyplot as plt
from datetime import datetime
#plotting libraries
import matplotlib.image as mpimg
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
#reading csv in knmi.py
import csv
import pvlib
```

## Usage

```QGIS
under plugins PETS should be installed
directories should be referenced

for example:

#spatial information
directory_in : d:/project/run3/data/
directory_out : d:/project/run3/data/
label: run3sim10 

run3: testbed Rotterdam
sim10: 10:00
#dynamic information
weather csv is read

#calculation

fraction_area_buildings_treeregr.py
ndvi_infr_large.py
vegetation_footprints.py
skyview.py
urban_heat.py

pet_calculate.py

```

```python background

#--------------------------------
# fraction_area_buildings_treeregr.py
Purpose: calculating the wind formed by trees and buildings
Input: im1:building_mask.tiff , im2:building_height.tiff , im3:trees_ahn.tiff , im4:trees_mask.tiff 
Output: wind_2d.tiff 

import numpy as np
from PIL import Image
from .pet_parameters import window_footprint, writer
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite

Def FabuildingTree(stat, dyn, im1, im2, im3, im4):

#--------------------------------

# ndvi_infr_large.py
Purpose: calculating green areas in the city based on rgb and infr photos 
Input: rgb.tiff , infr.tiff , water_mask.tiff , tree_mask.tiff 
Output: ndvi.tiff , vegfra.tiff , ndvi_crop_mask.tiff , ndvi_tree_mask.tiff 

import numpy as np
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite

def Ndvi_infr_large(stat, dyn, rgb, infr, water_mask, tree_mask)
#--------------------------------

# vegetation_footprints.py
Purpose: calculating the vegetation footprints based on a wind window averaging
input: vegfra
output: vegfra_wind
import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite

def Vegetation_footprints(stat, dyn, im):

#--------------------------------

#skyview.py
Purpose: calculating the skyview footprints based on a wind window averaging
input: svf_1m.tiff 
output: svf_wind.tiff 

import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite

def Skyview_footprints(stat, dyn, im):

#--------------------------------

#urban_heat.py
Purpose: calculating the urbanity of the area 
input: vegfra_wind.tiff , svf_wind.tiff 
output: urban_heat.tiff 

import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite

def Urban_heat(stat, dyn, im1, im2):

#--------------------------------

#pet_calculate.py
Purpose: calculating the hourly pet values
input: wind.tiff , urban_heat.tiff , ndvi_crop_mask.tiff , ndvi_tree_mask.tiff , shadow.tiff , svf_mask.tiff , svf.tiff 
output: pet_hour.tiff 

import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite

def PET_calculate(stat, dyn, im1, im2, im3, im4, im5, im6, im7): 

#--------------------------------
# weather.py
Purpose: creating hourly csv from knmi hourly values https://daggegevens.knmi.nl/klimatologie/uurgegevens 
Input: hourly values txt file https://daggegevens.knmi.nl/klimatologie/uurgegevens
Output: set.csv for each hour

def writeknmicsv(basedirectory, subdirectory, filename, filenametmintmax):
def wind_direction(dd, FF):
def writesetup(basedirectory, subdirectory, filename):

#--------------------------------

#pet_parameters.py
Purpose: increasing the reprocudability of the script by placing the parameters central on one spot
Input: directory_main = 'c:/project/bench/'

Def writer(filename, header, arr):
Def wind_direction(dd, FF):
Def day_night(month, day, hour):
Def window_footprint(winddir, upwind, sidewind, downwind, nowind):

##spatial information paramaters, read in the csv
Class StatParameters():
	Def __init__(self, xmin, xmax, ymin, ymax, cellsize=1, station='herwijnen', station_lat=51.859, station_lon=5.146):
	Self.ymin
	Self.ymax
	Self.xmin
	Self.xmax
	Self.cellsize
	Self.station
	Self.station_lat
	Self.station_lon
	Self.directory_in = 'd:/project/run1/input/'
	Self.directory_out = 'd:/project/run1/sim1/'
	Self.label = 'run1sim1'

	Def Resize(self):
	Def Reader(self, filename):
	Def Writer(self, filename):

##dynamic weather information paramaters, read in the csv
Class DynParameters():
	Def __init__(self, Date=20150701, decade=1, hour=10, min = 0, TT=28, FF=6, dd=100, Q=794.4444444, Qdif=158.8888889,
                 sunalt=55.3, RH=48, diurn=0.03):
		self.Date
		self.decade
		self.year
		self.month
		self.day
		self.hour
		self.min
		self.TT
		self.FF
		self.Q
		self.Qdif
		self.sunalt
		self.RH
		self.daynight
		self.S
		self.Tmin
		self.Tmax
		self.U
		self.diurnalcycle 
		self.wind, self.WE, self.winddir = wind_direction(self.dd, self.FF)

	def Reader(self, filename)
	def Writer(self, filename)

#--------------------------------

## Contributing

At this moment this is a code viewable for members. If all members accept the code, this could be published

## License

PET simulator © 2023 by Marieke van Esch is licensed under CC BY-SA 4.0 (created with https://chooser-beta.creativecommons.org/ )
