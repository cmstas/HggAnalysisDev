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
    n_electrons = awkward.num(events.Electron[lepton_selections.select_electrons(events, debug)])
    n_muons = awkward.num(events.Muon[lepton_selections.select_muons(events, debug)])

    n_taus = awkward.num(events.Tau[tau_selections.select_taus(events, debug)])

    n_leptons_and_taus = n_electrons + n_muons + n_taus

    lep_tau_cut = n_leptons_and_taus >= 1
    events = events[lep_tau_cut]
    cut_diagnostics.add_cut(len(events), cut_name = "leptons and taus >= 1 cut")

    return events

def tth_leptonic_preselection(events, debug):
    cut_diagnostics = utils.CutDiagnostics(n_events_initial = len(events), debug = debug, cut_set = "[analysis_selections.py : tth_leptonic_preselection]")
    
    # Get number of electrons, muons
    n_electrons = awkward.num(events.Electron[lepton_selections.select_electrons(events, debug)])
    n_muons = awkward.num(events.Muon[lepton_selections.select_muons(events, debug)])
    
    n_leptons = n_electrons + n_muons
    
    
    # Get number of jets
    #TODO
    
    lep_cut = n_leptons >= 1
    
    events = events[lep_cut]
    cut_diagnostics.add_cut(len(events), cut_name = "leptons >= 1 cut")
    
    return events
