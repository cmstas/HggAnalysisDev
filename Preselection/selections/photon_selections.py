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

def diphoton_preselection(events, photons, options, debug):
    # Initialize cut diagnostics tool for debugging
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")

    selected_photons = photons[select_photons(events, photons, options, debug)]

    ### mgg cut ###
    resonant = options["resonant"]
    if resonant:
        mgg_mask = numpy.array(events.ggMass > 100) & numpy.array(events.ggMass < 180)
    else:
        sideband_low = numpy.array(events.ggMass > 100) & numpy.array(events.ggMass < 120)
        sideband_high = numpy.array(events.ggMass > 130) & numpy.array(events.ggMass < 180)
        mgg_mask = sideband_low | sideband_high

    ### pt/mgg cuts ###
    lead_pt_mgg_requirement = (selected_photons.pt / events.ggMass) > 0.33
    sublead_pt_mgg_requirement = (selected_photons.pt / events.ggMass) > 0.25

    lead_pt_mgg_cut = awkward.num(selected_photons[lead_pt_mgg_requirement]) >= 1 # at least 1 photon passing lead requirement
    sublead_pt_mgg_cut = awkward.num(selected_photons[sublead_pt_mgg_requirement]) >= 2 # at least 2 photon passing sublead requirement
    pt_mgg_cut = lead_pt_mgg_cut & sublead_pt_mgg_cut

    ### pho ID MVA cuts ###
    pho_idmva_requirement = selected_photons.mvaID > options["photons"]["idmva_cut"]
    pho_idmva_cut = awkward.num(selected_photons[pho_idmva_requirement]) >= 2 # both selected_photons must pass id mva requirement

    ### electron veto cut ###
    eveto_requirement = selected_photons.electronVeto == 1
    eveto_cut = awkward.num(selected_photons[eveto_requirement]) >= 2 # both selected_photons must pass eveto requirement

    ### 2 good selected_photons ###
    photon_cut = awkward.num(selected_photons) == 2 # can regain a few % of signal if we set to >= 2 (probably e's that are reconstructed as selected_photons)

    all_cuts = mgg_mask & pt_mgg_cut & pho_idmva_cut & eveto_cut & photon_cut
    cut_diagnostics.add_cuts([mgg_mask, pt_mgg_cut, pho_idmva_cut, eveto_cut, photon_cut, all_cuts], ["mgg in [100, 180]" if resonant else "mgg in [100, 120] or [130, 180]", "lead (sublead) pt/mgg > 0.33 (0.25)", "pho IDMVA > -0.7", "electron veto", "2 good photons", "all"])

    return events[all_cuts], selected_photons[all_cuts]

def select_photons(events, photons, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = photons, cut_set = "[photon_selections.py : select_photons]", debug = debug)
    
    pt_cut = photons.pt > 25
    eta_cut = abs(photons.eta) < 2.5
    pt_mgg_cut = (photons.pt / events.ggMass) >= 0.25
    idmva_cut = photons.mvaID > options["photons"]["idmva_cut"] 
    eveto_cut = photons.electronVeto == 1
    photon_cut = pt_cut & eta_cut & pt_mgg_cut & idmva_cut & eveto_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, pt_mgg_cut, idmva_cut, eveto_cut, photon_cut], ["pt > 25", "|eta| < 2.5", "pt/mgg", "idmva", "eveto", "all"])
    return photon_cut

def set_photons(events, photons, debug):
    events["lead_pho_ptmgg"] = photons.pt[:,0] / events.ggMass
    events["sublead_pho_ptmgg"] = photons.pt[:,1] / events.ggMass
    events["lead_pho_eta"] = photons.eta[:,0]
    events["sublead_pho_eta"] = photons.eta[:,1]
    events["lead_pho_idmva"] = photons.mvaID[:,0]
    events["sublead_pho_idmva"] = photons.mvaID[:,1]
    return events
