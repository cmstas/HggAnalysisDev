import awkward
import numpy
import numba
import math
import time

import selections.selection_utils as utils

PI = math.pi

@numba.njit
def deltaR(phi1, phi2, eta1, eta2):
    dR = float(0)
    d_phi = float(0)
    d_eta = float(0)

    d_phi = phi1 - phi2
    if d_phi > PI:
        d_phi = d_phi - (2*PI)
    elif d_phi < -PI:
        d_phi = d_phi + (2*PI)

    d_eta = numpy.abs(eta1 - eta2)
    dR = ((d_eta)**2 + (d_phi)**2)**(0.5)
    return dR

@numba.njit
def select_deltaR_raw(events, nEvents, obj1, n_obj1, obj2, n_obj2, threshold, mask_offsets, mask_contents, debug):
    """
    Selects objects from obj1 which at least dR > threshold
    away from all objects of obj2
    """

    for i in range(nEvents):
        mask_offsets[i+1] = mask_offsets[i] + n_obj1[i]
        for j in range(n_obj1[i]):
            mask_contents[mask_offsets[i] + j] = True
            for k in range(n_obj2[i]):
                dR = deltaR(obj1.phi[i][j], obj2.phi[i][k], obj1.eta[i][j], obj2.eta[i][k])
                if dR < threshold:
                    mask_contents[mask_offsets[i] + j] = False

    return mask_offsets, mask_contents

def select_deltaR(events, obj1, obj2, threshold, debug):
    if debug > 1:
        start = time.time()
    nEvents = len(events)
    n_obj1 = numpy.array(awkward.num(obj1), numpy.int64)
    n_obj2 = numpy.array(awkward.num(obj2), numpy.int64)
    mask_offsets = numpy.zeros(nEvents+1, numpy.int64)
    mask_contents = numpy.empty(awkward.sum(n_obj1), numpy.bool)

    if debug > 1:
        start = time.time()

    mask_offsets, mask_contents = select_deltaR_raw(events, nEvents, obj1, n_obj1, obj2, n_obj2, threshold, mask_offsets, mask_contents, debug)

    if debug > 1:
        elapsed_time = time.time() - start
        print("[object_selections.py] PERFORMANCE: time to execute select_deltaR: %.6f" % (elapsed_time)) 

    mask = awkward.Array(awkward.layout.ListOffsetArray64(awkward.layout.Index64(mask_offsets), awkward.layout.NumpyArray(mask_contents)))

    #if debug > 0:
    #    print("[object_selections.py] Number of objects before/after dR cut: %d/%d (%.3f)" % (awkward.sum(awkward.num(obj1)), awkward.sum(awkward.num(obj1[mask])), float(awkward.sum(awkward.num(obj1[mask]))) / float(awkward.sum(awkward.num(obj1)))))

    return mask 
