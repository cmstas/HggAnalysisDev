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

def diphoton_preselection(events, debug):
    # Initialize cut diagnostics tool for debugging
    cut_diagnostics = utils.CutDiagnostics(n_events_initial = len(events), debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")

    ### mgg cut ###
    mgg_mask = numpy.array(events.ggMass > 100) & numpy.array(events.ggMass < 180)
    events = events[mgg_mask]
    cut_diagnostics.add_cut(len(events), cut_name = "mgg cut")

    ### pt/mgg cuts ###
    lead_pt_mgg_requirement = (events.Photon.pt / events.ggMass) > 0.33
    sublead_pt_mgg_requirement = (events.Photon.pt / events.ggMass) > 0.25

    lead_pt_mgg_cut = awkward.num(events.Photon[lead_pt_mgg_requirement]) >= 1 # at least 1 photon passing lead requirement
    sublead_pt_mgg_cut = awkward.num(events.Photon[sublead_pt_mgg_requirement]) >= 2 # at least 2 photon passing sublead requirement
    pt_mgg_cut = lead_pt_mgg_cut & sublead_pt_mgg_cut
    events = events[pt_mgg_cut]
    cut_diagnostics.add_cut(len(events), cut_name = "pt/mgg cut")

    ### pho ID MVA cuts ###
    pho_idmva_requirement = events.Photon.mvaID > -0.7
    pho_idmva_cut = awkward.num(events.Photon[pho_idmva_requirement]) >= 2 # both photons must pass id mva requirement
    events = events[pho_idmva_cut]
    cut_diagnostics.add_cut(len(events), cut_name = "pho ID MVA cut")

    ### electron veto cut ###
    eveto_requirement = events.Photon.electronVeto == 1
    eveto_cut = awkward.num(events.Photon[eveto_requirement]) >= 2 # both photons must pass eveto requirement
    events = events[eveto_cut]
    cut_diagnostics.add_cut(len(events), cut_name = "eveto cut")

    ### 2 good photons ###
    photon_requirements = select_photons(events, debug)
    photon_cut = awkward.num(photon_requirements) >= 2
    events = events[photon_cut]
    cut_diagnostics.add_cut(len(events), cut_name = "2 good photons cut")
    
    return events

def select_photons(events, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = events.Photon, cut_set = "[photon_selections.py : select_photons]", debug = debug)
    
    pt_mgg_cut = (events.Photon.pt / events.ggMass) >= 0.25
    idmva_cut = events.Photon.mvaID > -0.7
    eveto_cut = events.Photon.electronVeto == 1
    photon_cut = pt_mgg_cut & idmva_cut & eveto_cut

    cut_diagnostics.add_cuts([pt_mgg_cut, idmva_cut, eveto_cut, photon_cut], ["pt/mgg", "idmva", "eveto", "all"])
    return photon_cut

def set_photons(events, debug):
    events["lead_pho_ptmgg"] = events.Photon.pt[:,0] / events.ggMass
    events["sublead_pho_ptmgg"] = events.Photon.pt[:,1] / events.ggMass
    events["lead_pho_eta"] = events.Photon.eta[:,0]
    events["sublead_pho_eta"] = events.Photon.eta[:,1]
    events["lead_pho_idmva"] = events.Photon.mvaID[:,0]
    events["sublead_pho_idmva"] = events.Photon.mvaID[:,1]
    return events
