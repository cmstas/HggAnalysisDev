import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections
import selections.lepton_selections as lepton_selections
import selections.tau_selections as tau_selections
import selections.photon_selections as photon_selections

def ggTauTau_inclusive_preselection(events, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : ggTauTau_inclusive_preselection]")

    # Get number of electrons, muons, taus
    electron_selection = lepton_selections.select_electrons(events, events.Photon, options, debug)
    muon_selection = lepton_selections.select_muons(events, events.Photon, options, debug)
    tau_selection = tau_selections.select_taus(events, events.Photon, events.Muon[muon_selection], events.Electron[electron_selection], options, debug) 
    
    n_electrons = awkward.num(events.Electron[electron_selection])
    n_muons = awkward.num(events.Muon[muon_selection])
    n_taus = awkward.num(events.Tau[tau_selection])
    
    # Require >= 1 lep/tau
    n_leptons_and_taus = n_electrons + n_muons + n_taus
    lep_tau_cut = n_leptons_and_taus >= options["n_leptons_and_taus"] 

    # Require OS leptons/taus for events with 2 leptons/taus
    sum_charge = awkward.sum(events.Electron[electron_selection].charge, axis=1) + awkward.sum(events.Muon[muon_selection].charge, axis=1) + awkward.sum(events.Tau[tau_selection].charge, axis=1)
    charge_cut = sum_charge == 0
    two_leptons = n_leptons_and_taus == 2
    not_two_leptons = n_leptons_and_taus != 2
    os_cut = (two_leptons & charge_cut) | not_two_leptons # only require 2 OS leptons if there are ==2 leptons in the event

    all_cuts = lep_tau_cut & os_cut
    cut_diagnostics.add_cuts([lep_tau_cut, os_cut, all_cuts], ["N_leptons + N_taus >= 1", "OS dileptons", "all"])

    events = events[all_cuts]

    return events

def tth_leptonic_preselection(events, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : tth_leptonic_preselection]")
    
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
