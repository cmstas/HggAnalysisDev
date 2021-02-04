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

def diphoton_preselection(events, resonant, debug):
    # Initialize cut diagnostics tool for debugging
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")

    photons = events.Photon[select_photons(events, debug)]

    ### mgg cut ###
    if resonant:
        mgg_mask = numpy.array(events.ggMass > 100) & numpy.array(events.ggMass < 180)
    else:
        sideband_low = numpy.array(events.ggMass > 100) & numpy.array(events.ggMass < 120)
        sideband_high = numpy.array(events.ggMass > 130) & numpy.array(events.ggMass < 180)
        mgg_mask = sideband_low | sideband_high

    ### pt/mgg cuts ###
    lead_pt_mgg_requirement = (photons.pt / events.ggMass) > 0.33
    sublead_pt_mgg_requirement = (photons.pt / events.ggMass) > 0.25

    lead_pt_mgg_cut = awkward.num(photons[lead_pt_mgg_requirement]) >= 1 # at least 1 photon passing lead requirement
    sublead_pt_mgg_cut = awkward.num(photons[sublead_pt_mgg_requirement]) >= 2 # at least 2 photon passing sublead requirement
    pt_mgg_cut = lead_pt_mgg_cut & sublead_pt_mgg_cut

    ### pho ID MVA cuts ###
    pho_idmva_requirement = photons.mvaID > -0.7
    pho_idmva_cut = awkward.num(photons[pho_idmva_requirement]) >= 2 # both photons must pass id mva requirement

    ### electron veto cut ###
    eveto_requirement = photons.electronVeto == 1
    eveto_cut = awkward.num(photons[eveto_requirement]) >= 2 # both photons must pass eveto requirement

    ### 2 good photons ###
    photon_cut = awkward.num(photons) == 2 # can regain a few % of signal if we set to >= 2 (probably e's that are reconstructed as photons)

    all_cuts = mgg_mask & pt_mgg_cut & pho_idmva_cut & eveto_cut & photon_cut
    cut_diagnostics.add_cuts([mgg_mask, pt_mgg_cut, pho_idmva_cut, eveto_cut, photon_cut, all_cuts], ["mgg in [100, 180]" if resonant else "mgg in [100, 120] or [130, 180]", "lead (sublead) pt/mgg > 0.33 (0.25)", "pho IDMVA > -0.7", "electron veto", "2 good photons", "all"])

    events = events[all_cuts]

    return events

def select_photons(events, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Photon, cut_set = "[photon_selections.py : select_photons]", debug = debug)
    
    pt_cut = events.Photon.pt > 25
    eta_cut = abs(events.Photon.eta) < 2.5
    pt_mgg_cut = (events.Photon.pt / events.ggMass) >= 0.25
    idmva_cut = events.Photon.mvaID > -0.7
    eveto_cut = events.Photon.electronVeto == 1
    photon_cut = pt_cut & eta_cut & pt_mgg_cut & idmva_cut & eveto_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, pt_mgg_cut, idmva_cut, eveto_cut, photon_cut], ["pt > 25", "|eta| < 2.5", "pt/mgg", "idmva", "eveto", "all"])
    return photon_cut

def set_photons(events, debug):
    events["lead_pho_ptmgg"] = events.Photon.pt[:,0] / events.ggMass
    events["sublead_pho_ptmgg"] = events.Photon.pt[:,1] / events.ggMass
    events["lead_pho_eta"] = events.Photon.eta[:,0]
    events["sublead_pho_eta"] = events.Photon.eta[:,1]
    events["lead_pho_idmva"] = events.Photon.mvaID[:,0]
    events["sublead_pho_idmva"] = events.Photon.mvaID[:,1]
    return events
