import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite
import pandas as pd

#------------------
# urbanheat
# python code: urban_heat
# input: vegfra_wind, svf_wind
# output: urban_heat

def Urban_heat(stat, dyn, im1, im2):

    print('Urban_heat.Calculator')

    S = dyn.S
    U = dyn.U
    Tmin = dyn.Tmin
    Tmax = dyn.Tmax

    vegfra, meta = GeotifToArray(im1, 1)
    svf, meta = GeotifToArray(im2, 1)
    h = np.shape(vegfra)[0]  # y
    w = np.shape(vegfra)[1]  # x
    uhi = np.ones((h, w))
    uhi *= 2
    uhi = uhi - vegfra - svf
    factor = (S * (Tmax - Tmin) ** 3 / U) ** (1 / 4)
    uhi *= factor
    im3 = ArrayToGeotif(uhi, meta)
    vegfra = svf = None

    return im3


