import awkward
import numpy
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

def select_photons(events, photons, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = photons, cut_set = "[photon_selections.py : select_photons]", debug = debug)
    
    pt_cut = photons.pt > options["photons"]["pt"]

    eta_cut1 = abs(photons.eta) < options["photons"]["eta"] 
    eta_cut2 = abs(photons.eta) < options["photons"]["transition_region_eta"][0]
    eta_cut3 = abs(photons.eta) > options["photons"]["transition_region_eta"][1]
    eta_cut = eta_cut1 & (eta_cut2 | eta_cut3)

    pt_mgg_cut = (photons.pt / events.ggMass) >= options["photons"]["sublead_pt_mgg_cut"]
    idmva_cut = photons.mvaID > options["photons"]["idmva_cut"] 
    eveto_cut = photons.electronVeto >= options["photons"]["eveto_cut"]
    photon_cut = pt_cut & eta_cut & pt_mgg_cut & idmva_cut & eveto_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, pt_mgg_cut, idmva_cut, eveto_cut, photon_cut], ["pt > 25", "|eta| < 2.5", "pt/mgg", "idmva", "eveto", "all"])
    return photon_cut

#TODO: finish full diphoton preselection for sync purposes
def select_photons_full(events, photons, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = photons, cut_set = "[photon_selections.py : select_photons]", debug = debug)

    pt_cut = photons.pt > options["photons"]["pt"]

    eta_cut1 = abs(photons.eta) < options["photons"]["eta"]
    eta_cut2 = abs(photons.eta) < options["photons"]["transition_region_eta"][0]
    eta_cut3 = abs(photons.eta) > options["photons"]["transition_region_eta"][1]
    eta_cut = eta_cut1 & (eta_cut2 | eta_cut3)

    pt_mgg_cut = (photons.pt / events.ggMass) >= options["photons"]["sublead_pt_mgg_cut"]
    idmva_cut = photons.mvaID > options["photons"]["idmva_cut"]
    eveto_cut = photons.electronVeto == 1

    #r9_iso_cut = photon_r9_iso_cuts(photons)

    #hlt_cut = photon_hlt_cuts(photons)


    return photon_cut



def photon_r9_iso_cuts(photons):
    return

def photon_hlt_cuts(photons):
    nEvents = len(photons)

    for i in range(nEvents):
        nPhotons = len(photons[i])
        for j in range(nPhotons):
            continue

    return  


def photon_eff_area(eta):
    """
    Values copied from https://github.com/cms-analysis/flashgg/blob/af2080a888a5013a14104fb46b5e97fadbbad811/Taggers/python/flashggPreselectedDiPhotons_cfi.py#L3
    """
    if eta < 1.5:
        return 0.16544
    else:
        return 0.13212

def set_photons(events, photons, debug):
    events["lead_pho_ptmgg"] = photons.pt[:,0] / events.ggMass
    events["sublead_pho_ptmgg"] = photons.pt[:,1] / events.ggMass
    events["lead_pho_eta"] = photons.eta[:,0]
    events["sublead_pho_eta"] = photons.eta[:,1]
    events["lead_pho_idmva"] = photons.mvaID[:,0]
    events["sublead_pho_idmva"] = photons.mvaID[:,1]
    return events
