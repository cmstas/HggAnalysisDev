import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections
import selections.lepton_selections as lepton_selections
import selections.tau_selections as tau_selections
import selections.photon_selections as photon_selections

def ggTauTau_inclusive_preselection(events, debug):
    cut_diagnostics = utils.CutDiagnostics(n_events_initial = len(events), debug = debug, cut_set = "[analysis_selections.py : ggTauTau_inclusive_preselection]")

    # Get number of electrons, muons, taus
    n_electrons = awkward.num(lepton_selections.select_electrons(events, debug))

    lep_cut = n_electrons >= 1
    events = events[lep_cut]
    cut_diagnostics.add_cut(len(events), cut_name = "electron >= 1 cut")

    return events

