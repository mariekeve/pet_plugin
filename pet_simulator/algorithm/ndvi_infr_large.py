import numpy as np
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite
#-------------------------------------------------------------------------------------------------------------
# ndvi_infra_large
# purpose: create the ndvi from rgb and infr imagery
# input: lufo_rgb, lufo_infr, water_mask, tree_mask
# output: 'ndvi', 'vegfra', 'ndvi_crop_mask', ndvi_tree_mask'
#-------------------------------------------------------------------------------------------------------------
def Ndvi_infr_large(stat_parameters, dyn_parameters, rgb, infr, water_mask, tree_mask):

    print('Ndvi_infr_large.Calculator')

    wind_2d = np.zeros(shape=(0, 3))

    xmin = stat_parameters.xmin
    xmax = stat_parameters.xmax
    ymin = stat_parameters.ymin
    ymax = stat_parameters.ymax

    ndvi_infr_2d = np.zeros(shape=(0, 3))
    lufo_rgb, meta = GeotifToArray(rgb, 3)
    lufo_infr, meta = GeotifToArray(infr, 3)
    r = lufo_rgb[:, :, 0].astype(int)
    g = lufo_rgb[:, :, 1].astype(int)
    b = lufo_rgb[:, :, 2].astype(int)
    infr = lufo_infr[:, :, 0].astype(int)
    ndvi_infr = (infr - r) / (infr + r)
    ndvi_infr[ndvi_infr < 0] = 0
    arr = ndvi_infr

    im1 = ArrayToGeotif(arr, meta)
    h = meta[3]
    w = meta[4]

    water_mask, meta = GeotifToArray(water_mask, 1)
    day = np.zeros((h, w), dtype=float)
    night = np.zeros((h, w), dtype=float)
    for i in range(h):
        for j in range(w):
            if arr[i, j] > 0.16:
                night[i, j] = 1
                day[i, j] = 1
            if water_mask[i, j] == 1:
                night[i, j] = 0
                day[i, j] = 1

    if dyn_parameters.daynight == 'day':
        im2 = ArrayToGeotif(day, meta)
    elif dyn_parameters.daynight == 'night':
        im2 = ArrayToGeotif(night, meta)

    tree_mask, meta = GeotifToArray(tree_mask, 1)

    crop = np.copy(night)
    tree = np.copy(night)

    for i in range(h):
        for j in range(w):
            if night[i, j] == 1:
                if tree_mask[i, j] == 1:
                    crop[i, j] = 0
                else:
                    tree[i, j] = 0

    im3 = ArrayToGeotif(crop, meta)
    im4 = ArrayToGeotif(tree, meta)

    arr = day = night = tree = crop = None
    return im1, im2, im3, im4



