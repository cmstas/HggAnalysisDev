import awkward
import numpy
import numba
import math
import time

import selections.selection_utils as utils

PI = math.pi

def compute_deltaR(phi1, phi2, eta1, eta2):
    d_phi = numpy.array(phi1 - phi2)
    for i in range(len(d_phi)):
        if d_phi[i] > PI:
            d_phi[i] = d_phi[i] - (2*PI)
        elif d_phi[i] < -PI:
            d_phi[i] = d_phi[i] + (2*PI)

    d_eta = numpy.abs(eta1 - eta2)
    dR = ((d_eta)**2 + (d_phi)**2)**(0.5)
    return dR

#TODO: make compatible with vectors (quick, unoptimized implementation above)
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

    mask_offsets, mask_contents = select_deltaR_raw(events, nEvents, obj1, n_obj1, obj2, n_obj2, threshold, mask_offsets, mask_contents, debug)

    if debug > 1:
        elapsed_time = time.time() - start
        print("[object_selections.py] PERFORMANCE: time to execute select_deltaR: %.6f" % (elapsed_time)) 

    mask = awkward.Array(awkward.layout.ListOffsetArray64(awkward.layout.Index64(mask_offsets), awkward.layout.NumpyArray(mask_contents)))

    return mask

@numba.njit
def inv_mass(pt1, eta1, phi1, pt2, eta2, phi2):
    """
    Assumes massless particles (ok for photons/eles, probably need to update for heavier particles)
    """
    mass = float(0)
    mass = numpy.sqrt(2 * pt1 * pt2 * (numpy.cosh(eta1 - eta2) - numpy.cos(phi1 - phi2)))
    return mass

@numba.njit
def select_mass_raw(events, nEvents, obj1, n_obj1, obj2, n_obj2, mass_low, mass_high, mask_offsets, mask_contents, debug):
    """
    Select object from obj1 which have invariant masses outside "mass_range"
    with respect to all objects in obj2
    """

    for i in range(nEvents):
        mask_offsets[i+1] = mask_offsets[i] + n_obj1[i]
        for j in range(n_obj1[i]):
            mask_contents[mask_offsets[i] + j] = True
            for k in range(n_obj2[i]):
                mass = inv_mass(obj1[i][j].pt, obj1[i][j].eta, obj1[i][j].phi, obj2[i][k].pt, obj2[i][k].eta, obj2[i][k].phi)
                if mass > mass_low and mass < mass_high:
                    mask_contents[mask_offsets[i] + j] = False
    return mask_offsets, mask_contents

def select_mass(events, obj1, obj2, mass_range, debug):
    if debug > 1:
        start = time.time()

    nEvents = len(events)
    n_obj1 = numpy.array(awkward.num(obj1), numpy.int64)
    n_obj2 = numpy.array(awkward.num(obj2), numpy.int64)
    mask_offsets = numpy.zeros(nEvents+1, numpy.int64)
    mask_contents = numpy.empty(awkward.sum(n_obj1), numpy.bool)

    mass_low = float(mass_range[0])
    mass_high = float(mass_range[1])

    mask_offsets, mask_contents = select_mass_raw(events, nEvents, obj1, n_obj1, obj2, n_obj2, mass_low, mass_high, mask_offsets, mask_contents, debug)

    if debug > 1:
        elapsed_time = time.time() - start
        print("[object_selections.py] PERFORMANCE: time to execute select_mass: %.6f" % (elapsed_time))

    mask = awkward.Array(awkward.layout.ListOffsetArray64(awkward.layout.Index64(mask_offsets), awkward.layout.NumpyArray(mask_contents)))

    return mask
 
