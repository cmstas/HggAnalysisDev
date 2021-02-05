import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections

def select_electrons(events, photons, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Electron, cut_set = "[lepton_selections.py : select_electrons]", debug = debug)

    pt_cut = events.Electron.pt > options["electrons"]["pt"]
    eta_cut = abs(events.Electron.eta) < options["electrons"]["eta"]
    ip_xy_cut = abs(events.Electron.dxy) < options["electrons"]["ip_xy"]
    ip_z_cut = abs(events.Electron.dz) < options["electrons"]["ip_z"]
    id_cut = (events.Electron.mvaFall17V2Iso_WP90 == True | ((events.Electron.mvaFall17V2noIso_WP90 == True) & (events.Electron.pfRelIso03_all < 0.3)))
    # TODO: make ID cut configurable
    # also: ID cut has pretty low efficiency on signal, loosen?
    dR_cut = object_selections.select_deltaR(events, events.Electron, photons, options["electrons"]["dR_pho"], debug)

    electron_cut = pt_cut & eta_cut & ip_xy_cut & ip_z_cut & id_cut & dR_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, ip_xy_cut, ip_z_cut, id_cut, dR_cut, electron_cut], ["pt", "eta", "ip_xy", "ip_z", "id", "dR", "all"])

    return electron_cut

def select_muons(events, photons, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Muon, cut_set = "[lepton_selections.py : select_muons]", debug = debug)

    pt_cut = events.Muon.pt > options["muons"]["pt"]
    eta_cut = abs(events.Muon.eta) < options["muons"]["eta"]
    ip_xy_cut = abs(events.Muon.dxy) < options["muons"]["ip_xy"]
    ip_z_cut = abs(events.Muon.dz) < options["muons"]["ip_z"]
    iso_cut = events.Muon.pfRelIso03_all < options["muons"]["rel_iso"]
    dR_cut = object_selections.select_deltaR(events, events.Muon, photons, options["muons"]["dR_pho"], debug)

    muon_cut = pt_cut & eta_cut & ip_xy_cut & ip_z_cut & iso_cut & dR_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, ip_xy_cut, ip_z_cut, iso_cut, dR_cut, muon_cut], ["pt", "eta", "ip_xy", "ip_z", "iso", "dR", "all"])

    return muon_cut

def set_electrons(events, debug):
    events["n_electrons"] = awkward.num(events.Electron)

    electron_pt_padded = utils.pad_awkward_array(events.Electron.pt, 2, -9)
    electron_eta_padded = utils.pad_awkward_array(events.Electron.eta, 2, -9)
    electron_phi_padded = utils.pad_awkward_array(events.Electron.phi, 2, -9)
    electron_mass_padded = utils.pad_awkward_array(events.Electron.mass, 2, -9)

    events["ele1_pt"] = electron_pt_padded[:,0]
    events["ele2_pt"] = electron_pt_padded[:,1]
    events["ele1_eta"] = electron_eta_padded[:,0]
    events["ele2_eta"] = electron_eta_padded[:,1]
    events["ele1_phi"] = electron_phi_padded[:,0]
    events["ele2_phi"] = electron_phi_padded[:,1]
    events["ele1_mass"] = electron_mass_padded[:,0]
    events["ele2_mass"] = electron_mass_padded[:,1]

    return events

def set_muons(events, debug):
    events["n_muons"] = awkward.num(events.Muon)

    muon_pt_padded = utils.pad_awkward_array(events.Muon.pt, 2, -9)
    muon_eta_padded = utils.pad_awkward_array(events.Muon.eta, 2, -9)
    muon_phi_padded = utils.pad_awkward_array(events.Muon.phi, 2, -9)
    muon_mass_padded = utils.pad_awkward_array(events.Muon.mass, 2, -9)
    
    events["muon1_pt"] = muon_pt_padded[:,0]
    events["muon2_pt"] = muon_pt_padded[:,1]
    events["muon1_eta"] = muon_eta_padded[:,0]
    events["muon2_eta"] = muon_eta_padded[:,1]
    events["muon1_phi"] = muon_phi_padded[:,0]
    events["muon2_phi"] = muon_phi_padded[:,1]
    events["muon1_mass"] = muon_mass_padded[:,0]
    events["muon2_mass"] = muon_mass_padded[:,1] 

    return events

#TODO: implement varying definitions for leptons (e.g. "Loose", "Medium", "Tight") 
