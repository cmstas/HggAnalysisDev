import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections

DR_TAU_PHO = 0.2
DR_TAU_LEP = 0.4

def select_taus(events, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Tau, cut_set = "[tau_selections.py : select_taus]", debug = debug)

    pt_cut = events.Tau.pt > 10
    eta_cut = abs(events.Tau.eta) < 2.3
    decay_mode_cut = events.Tau.idDecayModeNewDMs == True
    dz_cut = abs(events.Tau.dz) < 0.2

    id_electron_cut = events.Tau.idDeepTau2017v2p1VSe >= 2
    id_muon_cut = events.Tau.idDeepTau2017v2p1VSmu >= 1
    id_jet_cut = events.Tau.idDeepTau2017v2p1VSjet >= 8

    dR_pho_cut = object_selections.select_deltaR(events, events.Tau, events.Photon, DR_TAU_PHO, debug) 
    dR_muon_cut = object_selections.select_deltaR(events, events.Tau, events.Muon, DR_TAU_LEP, debug) 
    dR_ele_cut = object_selections.select_deltaR(events, events.Tau, events.Electron, DR_TAU_LEP, debug) 

    tau_cut = pt_cut & eta_cut & decay_mode_cut & dz_cut & id_electron_cut & id_muon_cut & id_jet_cut & dR_pho_cut & dR_muon_cut & dR_ele_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, decay_mode_cut, dz_cut, id_electron_cut, id_muon_cut, id_jet_cut, dR_pho_cut, dR_muon_cut, dR_ele_cut, tau_cut], ["pt", "eta", "decay mode", "dz", "DeepTau vs ele", "DeepTau vs mu", "DeepTau vs jet", "dR tau vs. pho", "dR tau vs. muon", "dR tau vs. ele", "all"])

    return tau_cut

def set_taus(events, debug):
    events["n_tau"] = awkward.num(events.Tau)

    tau_pt_padded = utils.pad_awkward_array(events.Tau.pt, 2, -9)
    tau_eta_padded = utils.pad_awkward_array(events.Tau.eta, 2, -9)
    tau_phi_padded = utils.pad_awkward_array(events.Tau.phi, 2, -9)
    tau_mass_padded = utils.pad_awkward_array(events.Tau.mass, 2, -9)
    tau_IDvsElec_padded = utils.pad_awkward_array(events.Tau.idDeepTau2017v2p1VSe, 2, -9)
    tau_IDvsJet_padded = utils.pad_awkward_array(events.Tau.idDeepTau2017v2p1VSjet, 2, -9)
    tau_IDvsMuon_padded = utils.pad_awkward_array(events.Tau.idDeepTau2017v2p1VSmu, 2, -9)

    events["tau1_pt"] = tau_pt_padded[:,0]
    events["tau2_pt"] = tau_pt_padded[:,1]
    events["tau1_eta"] = tau_eta_padded[:,0]
    events["tau2_eta"] = tau_eta_padded[:,1]
    events["tau1_phi"] = tau_phi_padded[:,0]
    events["tau2_phi"] = tau_phi_padded[:,1]
    events["tau1_mass"] = tau_mass_padded[:,0]
    events["tau2_mass"] = tau_mass_padded[:,1] 

    events["tau1_id_vs_e"] = tau_IDvsElec_padded[:,0]
    events["tau2_id_vs_e"] = tau_IDvsElec_padded[:,1]
    events["tau1_id_vs_m"] = tau_IDvsMuon_padded[:,0]
    events["tau2_id_vs_m"] = tau_IDvsMuon_padded[:,1]
    events["tau1_id_vs_j"] = tau_IDvsJet_padded[:,0]
    events["tau2_id_vs_j"] = tau_IDvsJet_padded[:,1]    

    return events
