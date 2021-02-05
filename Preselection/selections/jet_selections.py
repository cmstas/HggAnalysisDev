import awkward
import numpy
import numba 

import selections.selection_utils as utils
import selections.object_selections as object_selections

def select_jets(events, photons, electrons, muons, taus, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Jet, cut_set = "[jet_selections.py : select_jets]", debug = debug)

    pt_cut = events.Jet.pt > options["jets"]["pt"]
    eta_cut = abs(events.Jet.eta) < options["jets"]["eta"]

    dR_pho_cut = object_selections.select_deltaR(events, events.Jet, photons, options["jets"]["dR_pho"], debug)
    dR_ele_cut = object_selections.select_deltaR(events, events.Jet, electrons, options["jets"]["dR_lep"], debug)
    dR_muon_cut = object_selections.select_deltaR(events, events.Jet, muons, options["jets"]["dR_lep"], debug)

    if taus is not None:
        dR_tau_cut = object_selections.select_deltaR(events, events.Jet, taus, options["jets"]["dR_tau"], debug)
    else:
        dR_tau_cut = object_selections.select_deltaR(events, events.Jet, photons, 0.0, debug) # dummy cut of all True

    jet_cut = pt_cut & eta_cut & dR_pho_cut & dR_ele_cut & dR_muon_cut & dR_tau_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, dR_pho_cut, dR_ele_cut, dR_muon_cut, dR_tau_cut, jet_cut], ["pt > 25", "|eta| < 2.4", "dR_photons", "dR_electrons", "dR_muons", "dR_taus", "all"])
    
    return jet_cut 
