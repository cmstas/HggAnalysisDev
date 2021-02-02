import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections

def select_taus(events, debug):
    pt_cut = events.Tau.pt > 10
    eta_cut = abs(events.Tau.eta) < 2.5

    tau_cut = pt_cut & eta_cut 
    return tau_cut
