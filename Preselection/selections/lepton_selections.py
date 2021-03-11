import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections

def select_electrons(events, photons, electrons, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = electrons, cut_set = "[lepton_selections.py : select_electrons]", debug = debug)

    pt_cut = electrons.pt > options["electrons"]["pt"]

    eta_cut1 = abs(electrons.eta) < options["electrons"]["eta"]
    eta_cut2 = abs(electrons.eta) < options["electrons"]["transition_region_eta"][0]
    eta_cut3 = abs(electrons.eta) > options["electrons"]["transition_region_eta"][1]
    eta_cut = eta_cut1 & (eta_cut2 | eta_cut3)

    ip_xy_cut = abs(electrons.dxy) < options["electrons"]["ip_xy"]
    ip_z_cut = abs(electrons.dz) < options["electrons"]["ip_z"]
    id_cut = electron_id(electrons, options)
    dR_cut = object_selections.select_deltaR(events, electrons, photons, options["electrons"]["dR_pho"], debug)
    mZ_cut = object_selections.select_mass(events, electrons, photons, options["electrons"]["mZ_cut"], debug)
    

    electron_cut = pt_cut & eta_cut & ip_xy_cut & ip_z_cut & id_cut & dR_cut & mZ_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, ip_xy_cut, ip_z_cut, id_cut, dR_cut, mZ_cut, electron_cut], ["pt", "eta", "ip_xy", "ip_z", "id", "dR", "m_egamma not in m_Z +/- 5 Gev", "all"])

    return electron_cut

def select_muons(events, photons, muons, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = muons, cut_set = "[lepton_selections.py : select_muons]", debug = debug)

    pt_cut = muons.pt > options["muons"]["pt"]
    eta_cut = abs(muons.eta) < options["muons"]["eta"]
    ip_xy_cut = abs(muons.dxy) < options["muons"]["ip_xy"]
    ip_z_cut = abs(muons.dz) < options["muons"]["ip_z"]
    id_cut = muon_id(muons, options)
    dR_cut = object_selections.select_deltaR(events, muons, photons, options["muons"]["dR_pho"], debug)

    muon_cut = pt_cut & eta_cut & ip_xy_cut & ip_z_cut & id_cut & dR_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, ip_xy_cut, ip_z_cut, id_cut, dR_cut, muon_cut], ["pt", "eta", "ip_xy", "ip_z", "id", "dR", "all"])

    return muon_cut

def set_electrons(events, electrons, debug):
    events["n_electrons"] = awkward.num(electrons)

    electron_pt_padded = utils.pad_awkward_array(electrons.pt, 2, -9)
    electron_eta_padded = utils.pad_awkward_array(electrons.eta, 2, -9)
    electron_phi_padded = utils.pad_awkward_array(electrons.phi, 2, -9)
    electron_mass_padded = utils.pad_awkward_array(electrons.mass, 2, -9)
    electron_tightID_padded = utils.pad_awkward_array(electrons.mvaFall17V2Iso_WP80, 2, -9)

    events["ele1_pt"] = electron_pt_padded[:,0]
    events["ele2_pt"] = electron_pt_padded[:,1]
    events["ele1_eta"] = electron_eta_padded[:,0]
    events["ele2_eta"] = electron_eta_padded[:,1]
    events["ele1_phi"] = electron_phi_padded[:,0]
    events["ele2_phi"] = electron_phi_padded[:,1]
    events["ele1_mass"] = electron_mass_padded[:,0]
    events["ele2_mass"] = electron_mass_padded[:,1]
    events["ele1_tightId"] = electron_tightID_padded[:,0]
    events["ele2_tightId"] = electron_tightID_padded[:,0]

    return events

def set_muons(events, muons, debug):
    events["n_muons"] = awkward.num(muons)

    muon_pt_padded = utils.pad_awkward_array(muons.pt, 2, -9)
    muon_eta_padded = utils.pad_awkward_array(muons.eta, 2, -9)
    muon_phi_padded = utils.pad_awkward_array(muons.phi, 2, -9)
    muon_mass_padded = utils.pad_awkward_array(muons.mass, 2, -9)
    muon_tightID_padded = utils.pad_awkward_array(muons.tightId, 2, -9)

    events["muon1_pt"] = muon_pt_padded[:,0]
    events["muon2_pt"] = muon_pt_padded[:,1]
    events["muon1_eta"] = muon_eta_padded[:,0]
    events["muon2_eta"] = muon_eta_padded[:,1]
    events["muon1_phi"] = muon_phi_padded[:,0]
    events["muon2_phi"] = muon_phi_padded[:,1]
    events["muon1_mass"] = muon_mass_padded[:,0]
    events["muon2_mass"] = muon_mass_padded[:,1] 
    events["muon1_tightId"] = muon_tightID_padded[:,0]
    events["muon2_tightId"] = muon_tightID_padded[:,1]

    return events

def electron_id(electrons, options):
    if options["electrons"]["id"] == "hh":
        cut = (electrons.mvaFall17V2Iso_WP90 == True | ((electrons.mvaFall17V2noIso_WP90 == True) & (electrons.pfRelIso03_all < 0.3)))
    elif options["electrons"]["id"] == "hig_19_013":
        id_cut = electrons.mvaFall17V2Iso_WP90 == True
        conversion_cut = electrons.convVeto == True
        cut = id_cut & conversion_cut
    return cut

def muon_id(muons, options):
    if options["electrons"]["id"] == "hh":
        iso_cut = muons.pfRelIso03_all < options["muons"]["rel_iso"] 
        id_cut = muons.pt > 0 # dummy selection, TODO: update muon id for hh->ggtautau
        cut = iso_cut & id_cut
    elif options["electrons"]["id"] == "hig_19_013":
        iso_cut = muons.miniPFRelIso_all < options["muons"]["rel_iso"]
        id_cut = muons.mediumId == True
        track_purity = muons.highPurity == True
        cut = iso_cut & id_cut & track_purity
    return cut

#TODO: implement varying definitions for leptons (e.g. "Loose", "Medium", "Tight") 
