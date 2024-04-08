import numpy as np
from PIL import Image
import multiprocessing as mp
from .pet_parameters import window_footprint, writer, wind_direction
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite, ArrayWrite
#-------------------------------------------------------------------------------------------------------------
# fractionareabuildingstreeregr
# purpose: calculate wind speed u1.2
# input: buildings_mask, buildings_height, trees_ahn, trees_mask
# output: wind_direction
#-------------------------------------------------------------------------------------------------------------

def meancal(a, size):

    mean = 0
    for j in range(size):
        mean += a[j]
    return mean / size

def myMean(A):

    m,n = A.shape
    pool = mp.Pool()
    rowMean = [pool.apply(meancal, args=(A[i,:], n)) for i in range(m)]
    mean = meancal(rowMean, m)
    pool.close()
    return mean

def FaBuildingTree(stat, dyn, im1, im2, im3, im4):

    print('FaBuildingTree.Calculator')

    #f = open('d:/tmp/aab.dat', 'wt')

    # parameters
    k = 0.4
    z0_grass = 0.03
    refwind = 1 / 0.63501
    red_grass = np.round(refwind * np.log(1.2 / z0_grass) / np.log(10 / z0_grass), 2)
    red_60_10 = np.log(10 / z0_grass) / np.log(60 / z0_grass)
    buildingfactor = 0.16 #was 0.6 #was 0.16
    treefactor = 0.27 #was 0.27
    winddir = dyn.winddir
    WE = dyn.WE
    wind_on = dyn.wind
    FF = dyn.FF

    # fine scale extended area = research area + boundary
    # size must by the same for im1, im2, im3, im4
    building_height_fine, meta1 = GeotifToArray(im1, 1)
    mask_building_fine, meta2 = GeotifToArray(im2, 1)
    tree_height_fine, meta3 = GeotifToArray(im3, 1)
    mask_tree_fine, meta4 = GeotifToArray(im4, 1)
    metafine = meta1

    # check fine scale extended area
    for i in range(metafine[3]):
        for j in range(metafine[4]):
            if building_height_fine[i,j] < 1e-3:
                building_height_fine[i, j] = 0
            else:
                mask_building_fine[i, j] = 1
            if tree_height_fine[i,j] < 1e-3:
                tree_height_fine[i, j] = 0
            else:
                mask_tree_fine[i, j] = 1



    # transform fine scale extended area to coarse scale extended area
    scale = int(stat.blocksize / stat.cellsize)
    nrow = int(metafine[3] / scale)
    ncol = int(metafine[4] / scale)
    meta = [metafine[0], metafine[1], stat.blocksize, nrow, ncol]
    building_height = np.zeros((meta[3], meta[4]))
    mask_building = np.zeros((meta[3], meta[4]))
    tree_height = np.zeros((meta[3], meta[4]))
    mask_tree = np.zeros((meta[3], meta[4]))
    building_weight = np.zeros((meta[3], meta[4]))
    tree_weight = np.zeros((meta[3], meta[4]))

    for i in range(meta[3]):
        istart = i * scale
        iend = istart + scale - 1
        iiend = iend
        if i < meta[3] - 1:
            iiend = iend + 1
        for j in range(meta[4]):
            jstart = j * scale
            jend = jstart + scale - 1
            jjend = jend
            if j < meta[4] - 1:
                jjend = jend + 1

            building_area = np.mean(mask_building_fine[istart: iend + 1, jstart: jend + 1])
            if building_area > 1e-2:
                building_height[i,j] = np.mean(building_height_fine[istart: iend + 1, jstart: jend + 1]) / building_area
                mask_building[i, j] = 1.0
            tree_area = np.mean(mask_tree_fine[istart: iend + 1, jstart: jend + 1])
            if tree_area > 1e-2:
                tree_height[i, j] = np.mean(tree_height_fine[istart: iend + 1, jstart: jend + 1]) / tree_area
                mask_tree[i, j] = 1

            if wind_on:
                if WE: # east-west or west-east wind
                    for m in range(istart, iend + 1, 1):
                        for n in range(jstart, jjend, 1):
                            building_weight[i, j] += abs(building_height_fine[m, n + 1] - building_height_fine[m, n]) * 0.5
                            tree_weight[i, j] += abs(tree_height_fine[m, n + 1] - tree_height_fine[m, n]) * 0.5

                else: # north-south or south-north wind
                    for n in range(jstart, jend + 1, 1):
                        for m in range(istart, iiend, 1):
                            building_weight[i, j] += abs(building_height_fine[m + 1, n] - building_height_fine[m, n]) * 0.5
                            tree_weight[i, j] += abs(tree_height_fine[m + 1, n] - tree_height_fine[m, n]) * 0.5

            else: # no wind
                for m in range(istart, iend + 1, 1):
                    for n in range(jstart, jjend, 1):
                        building_weight[i, j] += abs(building_height_fine[m, n + 1] - building_height_fine[m, n]) * 0.5
                        tree_weight[i, j] += abs(tree_height_fine[m, n + 1] - tree_height_fine[m, n]) * 0.5

                for n in range(jstart, jend + 1, 1):
                    for m in range(istart, iiend, 1):
                        building_weight[i, j] += abs(building_height_fine[m + 1, n] - building_height_fine[m, n]) * 0.5
                        tree_weight[i, j] += abs(tree_height_fine[m + 1, n] - tree_height_fine[m, n]) * 0.5

            #f.write(f'i {i} j {j} -> {istart} {iend} - {jstart} {jend} -> building {building_weight[i, j]} tree {tree_weight[i, j]}\n')



    #  research area coarse
    nrow = int(stat.nrow / scale)
    ncol = int(stat.ncol / scale)
    metadata = [stat.xmin, stat.ymin, stat.blocksize, nrow, ncol]
    wind_2d = np.zeros((nrow, ncol))

    # (moving) footprint area coarse
    jleft, jright, iup, idown = window_footprint(dyn.winddir, dyn.upwind, dyn.sidewind, dyn.downwind, dyn.nowind, stat.blocksize)
    total_area = (jleft + jright + 1) * (iup + idown + 1) * scale**2 # number of large blocks in footprint area

    # upper left cell of the research area in extended research area coordinates
    iref = int((stat.ymin - meta[1]) / meta[2])
    jref = int((stat.xmin - meta[0]) / meta[2])

    # calculate wind scaling map
    for i in range(nrow):
        istart = i + iref - idown
        iend = i + iref + iup
        for j in range(ncol):
            jstart = j + jref - jleft
            jend = j + jref + jright

            switch = False
            building_area = np.mean(mask_building[istart: iend + 1, jstart: jend + 1])
            tree_area = np.mean(mask_tree[istart: iend + 1, jstart: jend + 1])

            if building_area > 0:
                building_height_mean = np.mean(building_height[istart: iend + 1, jstart: jend + 1]) / building_area
                switch = True
            else:
                building_height_mean = 0

            if tree_area > 0:
                tree_height_mean = np.mean(tree_height[istart: iend + 1, jstart: jend + 1]) / tree_area
                tree_height_regr = np.max(7.721 * tree_height_mean ** 0.5, 0)
                switch = True
            else:
                tree_height_mean = 0
                tree_height_regr = 0

            if switch == True:
                height_com_pre = max((building_height_mean * building_area + tree_height_regr * tree_area * treefactor /
                                      buildingfactor) / (building_area + tree_area * treefactor / buildingfactor), 4)
            else:
                height_com_pre = 4.0

            # calculate building and tree fronts for a cell using its window (1 no blockage, 0 fully blocked)
            tree_front = 0
            building_front = 0

            for m in range(istart, iend + 1, 1):
                for n in range(jstart, jend + 1, 1):
                    building_front += building_weight[m, n] * buildingfactor
                    tree_front += tree_weight[m, n] * treefactor

            # fit for ahn tree to treefile (bomenbestand)
            tree_regr = 45.45 * (tree_front ** 0.5)
            front_regr = building_front + tree_regr

            if front_regr > 25 and switch:  # was 25  bij hele kleine oppervlakten gewoon op 0 laten, moet hoogte hebben zit ook in BW script
                height_com = max(height_com_pre, 4)
                lambda1 = min(front_regr / total_area + 0.015, 0.33)

                # frontal surface density
                if lambda1 < 0.08:
                    z0 = 0.048 * height_com # (surface roughness length)
                    d = 0.066 * height_com # (zero-plane displacement)
                    zw = 2 * height_com # (top of the roughness layer)
                    A = -0.35 * height_com # parameter for interpolation wind profile
                    B = 0.56 # parameter for interpolation wind profile
                elif lambda1 < 0.135:
                    z0 = 0.071 * height_com
                    d = 0.26 * height_com
                    zw = 2.5 * height_com
                    A = -0.35 * height_com
                    B = 0.50
                elif lambda1 < 0.18:
                    z0 = 0.084 * height_com
                    d = 0.32 * height_com
                    zw = 2.7 * height_com
                    A = -0.34 * height_com
                    B = 0.48
                elif lambda1 < 0.265:
                    z0 = 0.08 * height_com
                    d = 0.42 * height_com
                    zw = 1.5 * height_com
                    A = -0.56 * height_com
                    B = 0.66
                else:
                    z0 = 0.077 * height_com
                    d = 0.57 * height_com
                    zw = 1.2 * height_com
                    A = -0.85 * height_com
                    B = 0.92

                # some additional computations
                ustar = refwind / red_60_10 * k / np.log((60 - d) / z0)
                uzw = ustar / k * np.log((zw - d) / z0)
                uh = uzw - ustar / B * np.log((A + B * zw) / (A + B * height_com))
                wind_2d[i, j] = min(uh * np.exp(9.6 * lambda1 * (1.2 / height_com - 1)), red_grass)
            else:
                wind_2d[i, j] = red_grass

    im = ArrayToGeotif(wind_2d, metadata)
    building_height = tree_height = mask_tree = mask_building = wind_2d = wind_notree_2d = wind_tree_2d = None

    #f.close()

    return im