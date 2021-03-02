import awkward
import numpy
import numba

import selections.selection_utils as utils
from selections import photon_selections, object_selections

def diphoton_preselection(events, selected_photons, options, debug):
    # Initialize cut diagnostics tool for debugging
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")

    ### mgg cut ###
    resonant = options["resonant"]
    if resonant:
        mgg_mask = numpy.array(events.gg_mass > options["diphotons"]["mgg_lower"]) & numpy.array(events.gg_mass < options["diphotons"]["mgg_upper"])
    else:
        sideband_low = numpy.array(events.gg_mass > options["diphotons"]["mgg_lower"]) & numpy.array(events.gg_mass < options["diphotons"]["mgg_sideband_lower"])
        sideband_high = numpy.array(events.gg_mass > options["diphotons"]["mgg_sideband_upper"]) & numpy.array(events.gg_mass < options["diphotons"]["mgg_upper"])
        mgg_mask = sideband_low | sideband_high

    lead_pt_mgg_cut = selected_photons.pt[:,0] / events.gg_mass > options["photons"]["lead_pt_mgg_cut"]
    sublead_pt_mgg_cut = selected_photons.pt[:,1] / events.gg_mass > options["photons"]["sublead_pt_mgg_cut"]
    pt_mgg_cut = lead_pt_mgg_cut & sublead_pt_mgg_cut

    lead_idmva_cut = selected_photons.mvaID[:,0] > options["photons"]["idmva_cut"]
    sublead_idmva_cut = selected_photons.mvaID[:,1] > options["photons"]["idmva_cut"]
    idmva_cut = lead_idmva_cut & sublead_idmva_cut

    lead_eveto_cut = selected_photons.electronVeto[:,0] > options["photons"]["eveto_cut"]
    sublead_eveto_cut = selected_photons.electronVeto[:,1] > options["photons"]["eveto_cut"]
    eveto_cut = lead_eveto_cut & sublead_eveto_cut

    lead_eta_cut1 = abs(selected_photons.eta[:,0]) < options["photons"]["eta"]
    lead_eta_cut2 = abs(selected_photons.eta[:,0]) < options["photons"]["transition_region_eta"][0]
    lead_eta_cut3 = abs(selected_photons.eta[:,0]) > options["photons"]["transition_region_eta"][1]
    lead_eta_cut = lead_eta_cut1 & (lead_eta_cut2 | lead_eta_cut3)

    sublead_eta_cut1 = abs(selected_photons.eta[:,1]) < options["photons"]["eta"]
    sublead_eta_cut2 = abs(selected_photons.eta[:,1]) < options["photons"]["transition_region_eta"][0]
    sublead_eta_cut3 = abs(selected_photons.eta[:,1]) > options["photons"]["transition_region_eta"][1]
    sublead_eta_cut = sublead_eta_cut1 & (sublead_eta_cut2 | sublead_eta_cut3)

    eta_cut = lead_eta_cut & sublead_eta_cut

    if options["data"]:
        if options["year"] == 2016:
            trigger_cut = events.HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90 == True
        elif options["year"] == 2017 or options["year"] == 2018:
            trigger_cut = events.HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90 == True
    else:
        trigger_cut = events.gg_mass > 0

    all_cuts = mgg_mask & pt_mgg_cut & idmva_cut & eveto_cut & eta_cut & trigger_cut
    cut_diagnostics.add_cuts([mgg_mask, pt_mgg_cut, idmva_cut, eveto_cut, eta_cut, trigger_cut, all_cuts], ["mgg in [100, 180]" if resonant else "mgg in [100, 120] or [130, 180]", "lead (sublead) pt/mgg > 0.33 (0.25)", "pho idmva > -0.7", "eveto cut", "eta cut", "trigger", "all"])

    selected_events = events[all_cuts]
    selected_photons = selected_photons[all_cuts]

    # Calculate event-level photon/diphoton variables
    selected_events = photon_selections.set_photons(selected_events, selected_photons, debug)
    selected_events = set_diphotons(selected_events, selected_photons, debug) 

    return selected_events, selected_photons 

def set_diphotons(events, selected_photons, debug):
    events["diphoton_pt_mgg"] = events["gg_pt"] / events["gg_mass"]
    events["diphoton_rapidity"] = events["gg_eta"] # just using pseudorapidity, shouldn't be a big difference
    events["diphoton_delta_R"] = object_selections.compute_deltaR(
        selected_photons.phi[:,0],
        selected_photons.phi[:,1],
        selected_photons.eta[:,0],
        selected_photons.eta[:,1]
    )
    return events

def diphoton_preselection_old(events, photons, options, debug):
    # Initialize cut diagnostics tool for debugging
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")

    selected_photons = photons[photon_selections.select_photons(events, photons, options, debug)]

    ### mgg cut ###
    resonant = options["resonant"]
    if resonant:
        mgg_mask = numpy.array(events.gg_mass > options["diphotons"]["mgg_lower"]) & numpy.array(events.gg_mass < options["diphotons"]["mgg_upper"])
    else:
        sideband_low = numpy.array(events.gg_mass > options["diphotons"]["mgg_lower"]) & numpy.array(events.gg_mass < options["diphotons"]["mgg_sideband_lower"])
        sideband_high = numpy.array(events.gg_mass > options["diphotons"]["mgg_sideband_upper"]) & numpy.array(events.gg_mass < options["diphotons"]["mgg_upper"])
        mgg_mask = sideband_low | sideband_high

    ### pt/mgg cuts ###
    lead_pt_mgg_cut = selected_photons.pt[0] / events.gg_mass > options["photons"]["lead_pt_mgg_cut"]
    sublead_pt_mgg_cut = selected_photons.pt[1] / events.gg_mass > options["photons"]["sublead_pt_mgg_cut"]
    #lead_pt_mgg_requirement = (selected_photons.pt / events.gg_mass) > options["photons"]["lead_pt_mgg_cut"]
    #sublead_pt_mgg_requirement = (selected_photons.pt / events.gg_mass) > options["photons"]["sublead_pt_mgg_cut"]

    #lead_pt_mgg_cut = awkward.num(selected_photons[lead_pt_mgg_requirement]) >= 1 # at least 1 photon passing lead requirement
    #sublead_pt_mgg_cut = awkward.num(selected_photons[sublead_pt_mgg_requirement]) >= 2 # at least 2 photon passing sublead requirement
    pt_mgg_cut = lead_pt_mgg_cut & sublead_pt_mgg_cut

    ### 2 good selected_photons ###
    n_photon_cut = awkward.num(selected_photons) == 2 # can regain a few % of signal if we set to >= 2 (probably e's that are reconstructed as selected_photons)

    all_cuts = mgg_mask & pt_mgg_cut & n_photon_cut
    cut_diagnostics.add_cuts([mgg_mask, pt_mgg_cut, n_photon_cut, all_cuts], ["mgg in [100, 180]" if resonant else "mgg in [100, 120] or [130, 180]", "lead (sublead) pt/mgg > 0.33 (0.25)", "2 good photons", "all"])

    return events[all_cuts], selected_photons[all_cuts]

#TODO: finish full diphoton preselection for sync purposes
def diphoton_preselection_full(events, photons, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")

    selected_photons = photons[photon_selections.select_photons(events, photons, options, debug)]
