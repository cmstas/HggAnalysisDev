import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections

DR_LEP_PHO = 0.2

def select_electrons(events, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Electron, cut_set = "[lepton_selections.py : select_electrons]", debug = debug)

    pt_cut = events.Electron.pt > 10
    eta_cut = abs(events.Electron.eta) < 2.5
    ip_xy_cut = abs(events.Electron.dxy) < 0.045
    ip_z_cut = abs(events.Electron.dz) < 0.2
    id_cut = (events.Electron.mvaFall17V2Iso_WP90 == True | ((events.Electron.mvaFall17V2noIso_WP90 == True) & (events.Electron.pfRelIso03_all < 0.3)))
    dR_cut = object_selections.select_deltaR(events, events.Electron, events.Photon, DR_LEP_PHO, debug)

    electron_cut = pt_cut & eta_cut & ip_xy_cut & ip_z_cut & id_cut & dR_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, ip_xy_cut, ip_z_cut, id_cut, dR_cut, electron_cut], ["pt", "eta", "ip_xy", "ip_z", "id", "dR", "all"])

    return electron_cut

def select_muons(events, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Muon, cut_set = "[lepton_selections.py : select_muons]", debug = debug)

    pt_cut = events.Muon.pt > 10
    eta_cut = abs(events.Muon.eta) < 2.4
    ip_xy_cut = abs(events.Muon.dxy) < 0.045
    ip_z_cut = abs(events.Muon.dz) < 0.2
    iso_cut = events.Muon.pfRelIso03_all < 0.3
    dR_cut = object_selections.select_deltaR(events, events.Muon, events.Photon, DR_LEP_PHO, debug)

    muon_cut = pt_cut & eta_cut & ip_xy_cut & ip_z_cut & iso_cut & dR_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, ip_xy_cut, ip_z_cut, iso_cut, dR_cut, muon_cut], ["pt", "eta", "ip_xy", "ip_z", "iso", "dR", "all"])

    return muon_cut

#TODO: implement varying definitions for leptons (e.g. "Loose", "Medium", "Tight") 
