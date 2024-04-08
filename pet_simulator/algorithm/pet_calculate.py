#from IPython import get_ipython
#get_ipython().magic('reset -sf')

import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite
#-------------------------------------------------------------------------------------------------------------
# petcalculate
# purpose: calculate the PET
# input: shadow, urbanheat, wind, svf, svf_mask, ndvi_crop_mask, ndvi_tree_mask
# output: pets

def PET_calculate(stat, dyn, im1, im2, im3, im4, im5, im6, im7):

    TT = dyn.TT                 #TT:    Temperatuur (in 0.1 graden Celsius) op 1.50 m hoogte tijdens de waarneming
    FF = dyn.FF                 #FF:    Windsnelheid (in 0.1 m/s) gemiddeld over de laatste 10 minuten van het afgelopen uur
    Q = dyn.Q                   #Q:     Global solar irradiationGlobale straling (in J/cm2) per uurvak
    Qdif = dyn.Qdif             #Qdif:  Difuse radiation
    sunalt = dyn.sunalt         #sunalt:solar elevation angle
    RH = dyn.RH                 #RH:    Relative Humidity
    diurnal = dyn.diurnal       #diurnal correction factor UHI for Ta

    print('PET.Calculator')
    Bveg = 0.4
    Bnoveg = 3
    stef = 5.67 * 10 ** -8

    sun, meta = GeotifToArray(im1, 1)  # added anders geen ref in shadow
    urban, meta = GeotifToArray(im2, 1)
    wind, meta = GeotifToArray(im3, 1)
    svf, meta = GeotifToArray(im4, 1)
    svf_mask, meta = GeotifToArray(im5, 1)
    mask_vegfra, meta = GeotifToArray(im6, 1)
    trees_2m, meta = GeotifToArray(im7, 1)

    # with open("D:\\tmp\\test.txt", 'wt') as f:
    #     f.write(f"sun, meta {sun, meta}\\n")
    #     f.write(f"urban, meta {urban, meta}\\n")
    #     f.write(f"wind, meta {wind, meta}\\n")
    #     f.write(f"svf, meta {svf, meta}\\n")
    #     f.write(f"svf_mask, meta {svf_mask, meta}\\n")
    #     f.write(f"mask_vegfra, meta {mask_vegfra, meta}\\n")
    #     f.write(f"trees_2m, meta {trees_2m, meta}\\n")


    Ta = urban[:] * diurnal + TT
    Tw = TT * np.arctan(0.15198 * (RH + 8.3137) ** 0.5) + np.arctan(TT + RH) - np.arctan(
        RH - 1.676) + 0.0039184 * RH ** 1.5 * np.arctan(0.023101 * RH) - 4.686

    wind = ((wind - 0.125) * 0.5829 + 0.125) * FF
    wind[wind < 0.5] = 0.5
    wind_temp = np.ravel(wind)
    #wind_res = np.array(wind_temp).transpose()

    # day
    if Q > 0:
        sun_temp, meta = GeotifToArray(im1, 1)
        sun = sun_temp * (1 - trees_2m[:])

        PETshade = (-12.14 + 1.25 * Ta[:] - 1.47 * np.log(wind[:]) + 0.060 * Tw + 0.015 * svf[:] * Qdif +
                    0.0060 * (1 - svf[:]) * stef * (Ta[:] + 273.15) ** 4) * (1 - sun[:]) * svf_mask[:]
        PETveg = (-13.26 + 1.25 * Ta[:] + 0.011 * Q - 3.37 * np.log(
            wind[:]) + 0.078 * Tw + 0.0055 * Q * np.log(wind[:]) + 5.56 * np.sin(
            sunalt / 360 * 2 * np.pi) - 0.0103 * Q * np.log(wind[:]) * np.sin(
            sunalt / 360 * 2 * np.pi) + 0.546 * Bveg + 1.94 * svf[:]) * mask_vegfra[:] * sun[:] * svf_mask[:]
        PETnoveg = (-13.26 + 1.25 * Ta[:] + 0.011 * Q - 3.37 * np.log(
            wind[:]) + 0.078 * Tw + 0.0055 * Q * np.log(wind[:]) + 5.56 * np.sin(
            sunalt / 360 * 2 * np.pi) - 0.0103 * Q * np.log(wind[:]) * np.sin(
            sunalt / 360 * 2 * np.pi) + 0.546 * Bnoveg + 1.94 * svf[:]) * (1 - mask_vegfra[:]) * sun[:] * svf_mask[:]

        PET = PETshade + PETveg + PETnoveg

    # night
    else:
        PETshade = (-12.14 + 1.25 * Ta[:] - 1.47 * np.log(wind[:]) + 0.060 * Tw + 0.015 * svf[:] * Qdif
                    + 0.0060 * (1 - svf[:]) * stef * (Ta[:] + 273.15) ** 4) * (1 - sun[:]) * svf_mask[:]

        PET = PETshade

    im8 = ArrayToGeotif(PET, meta)
    sun = urban = wind = svf = svf_mask = mask_vegfra = trees_2m = PET = None

    return im8



