import awkward
import numpy as np

import numba

import selections.selection_utils as utils

"""
Notes: for some reason, event-level and object-level cuts seem to interfere with each other.
E.g. if I do
events = events[event_cut1]
events.Photon = events.Photon[object_cut1]
events = events[event_cut2]

events will regain some of the photons that were eliminated in object_cut1

For this reason, all selections should be done in the following way:
    1. Perform event-level selections (may include object-level quantities, e.g. 2 photons with pt/mgg > 0.25)
    2. Trim objects with object-level selections afterwards
"""


def create_selected_photons(photons, branches, debug):
    map = {}
    for branch in branches:
        if "selectedPhoton" not in branch:
            continue
        key = branch.replace("selectedPhoton_","")
        map[key] = photons[branch]

    selected_photons = awkward.zip(map)

    return selected_photons

def select_photons(events, photons, options, debug):

    pt_cut = photons.pt > options["photons"]["pt"]

    eta_cut1 = abs(photons.eta) < options["photons"]["eta"]
    eta_cut2 = abs(photons.eta) < options["photons"]["transition_region_eta"][0]
    eta_cut3 = abs(photons.eta) > options["photons"]["transition_region_eta"][1]
    eta_cut = eta_cut1 & (eta_cut2 | eta_cut3)

    idmva_cut = photons.mvaID > options["photons"]["idmva_cut"]
    eveto_cut = photons.electronVeto >= options["photons"]["eveto_cut"]
    photon_cut = pt_cut & eta_cut & idmva_cut & eveto_cut

    #cut_diagnostics.add_cuts([pt_cut, eta_cut, idmva_cut, eveto_cut, photon_cut], ["pt > 25", "|eta| < 2.5", "idmva", "eveto", "all"])
    return photon_cut

def set_photons(events, photons, debug):
    events["lead_pho_ptmgg"] = photons.pt[:,0] / events.gg_mass
    events["sublead_pho_ptmgg"] = photons.pt[:,1] / events.gg_mass
    events["lead_pho_eta"] = photons.eta[:,0]
    events["sublead_pho_eta"] = photons.eta[:,1]
    events["lead_pho_phi"] = photons.phi[:,0]
    events["sublead_pho_phi"] = photons.phi[:,1]
    events["lead_pho_idmva"] = photons.mvaID[:,0]
    events["sublead_pho_idmva"] = photons.mvaID[:,1]
    events["lead_pixelSeed"] = photons.pixelSeed[:,0]
    events["sublead_pixelSeed"] = photons.pixelSeed[:,1]
    return events
