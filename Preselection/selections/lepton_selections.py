import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections

def select_electrons(events, debug):
    pt_cut = events.Electron.pt > 10
    eta_cut = abs(events.Electron.eta) < 2.5
    ip_xy_cut = abs(events.Electron.dxy) < 0.045
    ip_z_cut = abs(events.Electron.dz) < 0.2
    id_cut = (events.Electron.mvaFall17V2Iso_WP90 == True | ((events.Electron.mvaFall17V2noIso_WP90 == True) & (events.Electron.pfRelIso03_all < 0.3)))
    dR_cut = object_selections.select_deltaR(events, events.Electron, events.Photon, 0.4, debug)

    electron_cut = pt_cut & eta_cut & ip_xy_cut & ip_z_cut & id_cut & dR_cut
    return electron_cut
