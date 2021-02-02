import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections

def select_taus(events, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Tau, cut_set = "[tau_selections.py : select_taus]", debug = debug)

    pt_cut = events.Tau.pt > 10
    eta_cut = abs(events.Tau.eta) < 2.3
    decay_mode_cut = events.Tau.idDecayModeNewDMs == True
    dz_cut = abs(events.Tau.dz) < 0.2

    id_electron_cut = events.Tau.idDeepTau2017v2p1VSe >= 1
    id_muon_cut = events.Tau.idDeepTau2017v2p1VSmu >= 1
    id_jet_cut = events.Tau.idDeepTau2017v2p1VSjet >= 1

    tau_cut = pt_cut & eta_cut & decay_mode_cut & dz_cut & id_electron_cut & id_muon_cut & id_jet_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, decay_mode_cut, dz_cut, id_electron_cut, id_muon_cut, id_jet_cut, tau_cut], ["pt", "eta", "decay mode", "dz", "DeepTau vs ele", "DeepTau vs mu", "DeepTau vs jet", "all"])

    return tau_cut
