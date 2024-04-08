import numpy as np
from PIL import Image
import pandas as pd

# sample files
data = np.random.randint(0, 255, (10,10)).astype(np.uint8)
im = Image.fromarray(data)
dataframe = pd.DataFrame()

from pet_parameters import StatParameters
from pet_parameters import DynParameters
from pet_parameters import directory_main

#-----------------------------------------------------------------------------------------------------------------------
# parameters

stat_parameters = StatParameters(172075, 176425, 440675, 444815)

# parameters
stat_parameters = StatParameters(xmin=172075, xmax=172075+6, ymin=440675, ymax=440675+5, cellsize=1, outsize=1,
        station='herwijnen', station_lat=51.859, station_lon=5.146, scenario='WH', verspringend=False)

dyn_parameters = DynParameters()

stat_parameters.Writer(f'{directory_main}Sat_parameters.csv')
dyn_parameters.Writer(f'{directory_main}Dyn_parameters.csv')

f = open(f'{directory_main}rawdata/out.txt', 'wt')
f.close()

#-----------------------------------------------------------------------------------------------------------------------
# fraction area buildings treeregr
# purpose: wind calculation
# outcome: wind_direction

from fraction_area_buildings_treeregr import FaBuildingTree
faBuildingTree = FaBuildingTree(stat_parameters, dyn_parameters)
faBuildingTree.Reader()
faBuildingTree.Calculator(stat_parameters, dyn_parameters)
faBuildingTree.Writer()

#-----------------------------------------------------------------------------------------------------------------------
# ndvi
# purpose: vegetation footprints and tree indication
# outcome: ndvi_trees_2m

from ndvi_infr_large import Ndvi_infr_large
ndvi_infr_large = Ndvi_infr_large(stat_parameters, dyn_parameters)
ndvi_infr_large.Reader()
ndvi_infr_large.Calculator(stat_parameters, dyn_parameters)
ndvi_infr_large.Writer()

#-----------------------------------------------------------------------------------------------------------------------
# vegetation footprints
# purpose: indication urban indicator
# outcome: Fveg_1m

from vegetation_footprints import Vegetation_footprints
vegetation_footprints = Vegetation_footprints(stat_parameters, dyn_parameters)
vegetation_footprints.Reader()
vegetation_footprints.Calculator(stat_parameters, dyn_parameters)
vegetation_footprints.Writer()

#-----------------------------------------------------------------------------------------------------------------------
# skyview factor
# purpose: indication urban indicator
# outcome: svf_1m

from skyview_footprints import SkyView
skyview_footprints = SkyView(stat_parameters, dyn_parameters)
skyview_footprints.Reader()
skyview_footprints.Calculator(stat_parameters, dyn_parameters)
skyview_footprints.Writer()

#-----------------------------------------------------------------------------------------------------------------------
# urban heat island
# purpose: combine geophysical data from skyview factor and vegetation footprint
# outcome: urban_morphology

from urban_heat import Urban_heat
urban_heat = Urban_heat(stat_parameters, dyn_parameters)
urban_heat.Reader()
urban_heat.Calculator(stat_parameters, dyn_parameters)
urban_heat.Writer()

#-----------------------------------------------------------------------------------------------------------------------
# pet calculation
# purpose: combine shadow + wind_direction + ndvi_trees_2m + urban morphology in order to calculate PET shade, PET veg, PET noveg
# outcome: PET{month}{day}{hour}

from pet_calculate import PET_calculate
pet_calculate = PET_calculate(stat_parameters, dyn_parameters)
pet_calculate.Reader()
pet_calculate.Calculator(stat_parameters, dyn_parameters)
pet_calculate.Writer()

#-----------------------------------------------------------------------------------------------------------------------
"""
dataframe.to_csv(f'{directory_main}weather/De_Bilt_1981_2010.csv')
dataframe.to_csv(f'{directory_main}weather/%sscenario.csv' % (parameters.scenario))
dataframe.to_csv(f'{directory_main}weather/De_Bilt_2004_2018.csv')
dataframe.to_csv(f'{directory_main}weather/Herwijnen_2004_2018.csv')
dataframe.to_csv(f'{directory_main}weather/THQ_Herwijnen_2004_2018.csv')

from transpose_angothour import Transpose_angothour
transpose_angothour = Transpose_angothour(parameters)
transpose_angothour.Reader()
#transpose_angothour.Calculator()
transpose_angothour.Writer()

# output f'{directory_main}knmi/new_THQF_Herwijnen2004_2018_%s_re.csv'
"""