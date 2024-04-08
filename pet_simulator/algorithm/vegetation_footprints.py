import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite
from numba import jit, prange
#-------------------------------------------------------------------------------------------------------------
# vegetation_footprint
# purpose: vegetation footprint calculation for urban heat map
# input: vegfra
# output: vegfra_2d
#-------------------------------------------------------------------------------------------------------------
#@jit(parallel=True)
def Vegetation_footprints(stat, dyn, im):

    print('Vegetation_footprints.Calculator')

    f = open('d:/tmp/veg.dat', 'wt')

    vegfra, meta = GeotifToArray(im, 1) # analyse gebied met randen

    nrow = int(stat.nrow * stat.cellsize / stat.blocksize)
    ncol = int(stat.ncol * stat.cellsize / stat.blocksize)
    metadata = [stat.xmin, stat.ymin, stat.blocksize, nrow, ncol]
    jleft, jright, iup, idown = window_footprint(dyn.winddir, dyn.upveg, dyn.sideveg, dyn.downveg, dyn.noveg, stat.blocksize)
    iref = int((stat.ymin - meta[1]) / meta[2])
    jref = int((stat.xmin - meta[0]) / meta[2])

    f.write(f'{metadata[0]} {metadata[1]} {metadata[2]} {metadata[3]} {metadata[4]}\n')
    f.write(f'{nrow} {ncol} {meta[0]} {meta[1]} {meta[2]} {meta[3]} {meta[4]}\n')
    f.write(f'{jleft} {jright} {iup} {idown} {iref} {jref}\n')
    f.close()

    vegfra_2d = np.zeros((nrow, ncol))
    for i in range(nrow):
        istart = i + iref - idown
        iend = i + iref + iup
        for j in range(ncol):
            jstart = j + jref - jleft
            jend = j + jref + jright
            vegfra_2d[i, j] = np.mean(vegfra[istart: iend+1, jstart: jend+1])

    im1 = ArrayToGeotif(vegfra_2d, metadata)
    vegfra_2d = None

    return im1
