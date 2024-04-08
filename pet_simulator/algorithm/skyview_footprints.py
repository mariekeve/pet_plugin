import numpy as np
from .pet_parameters import window_footprint
from .geotiff_creator import ArrayToGeotif, GeotifToArray, GeotifWrite
#-------------------------------------------------------------------------------------------------------------
# skyview_footprint
# purpose: skyview footprint calculation for urban heat map
# input: skyview
# output: skyview_2d
#-------------------------------------------------------------------------------------------------------------
def Skyview_footprints(stat, dyn, im):

    print('SkyView.Calculator')

    svf_2d = np.array(im)
    svf, meta = GeotifToArray(im, 1)                                        # analyse gebied met randen

    nrow = int(stat.nrow * stat.cellsize / stat.blocksize)
    ncol = int(stat.ncol * stat.cellsize / stat.blocksize)
    metadata = [stat.xmin, stat.ymin, stat.blocksize, nrow, ncol]
    jleft, jright, iup, idown = window_footprint(dyn.winddir, dyn.upveg, dyn.sideveg, dyn.downveg, dyn.noveg, stat.blocksize)
    iref = int((stat.ymin - meta[1]) / meta[2])
    jref = int((stat.xmin - meta[0]) / meta[2])
    h = nrow
    w = ncol

    mean_svf = np.zeros((h, w))
    for i in range(h):
        istart = i + iref - idown
        iend = i + iref + iup
        for j in range(w):
            jstart = j + jref - jleft
            jend = j + jref + jright
            perc = (np.mean(svf[istart: iend+1, jstart: jend+1]) > 0) / (np.sum(svf[istart: iend+1, jstart: jend+1]) > -1)
            if perc >= 0.2:
                mean_svf[i, j] = np.mean(svf[istart: iend+1, jstart: jend+1])
            elif perc >= 0.1:  # linearize between svf=1 for 0.1 and svf as executed above
                mean_pre_svf = np.mean(svf[istart: iend+1, jstart: jend+1])
                mean_svf[i, j] = ((perc - 0.1) / 0.1) * mean_pre_svf + (1 - (perc - 0.1) / 0.1) * 1
            else:
                mean_svf[i, j] = 1

    im1 = ArrayToGeotif(mean_svf, metadata)
    mean_svf = None

    return im1





