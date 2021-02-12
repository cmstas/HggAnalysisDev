import awkward
import numpy
import numba

import selections.selection_utils as utils
from selections import photon_selections

def diphoton_preselection(events, photons, options, debug):
    # Initialize cut diagnostics tool for debugging
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")

    selected_photons = photons[photon_selections.select_photons(events, photons, options, debug)]

    ### mgg cut ###
    resonant = options["resonant"]
    if resonant:
        mgg_mask = numpy.array(events.ggMass > options["diphotons"]["mgg_lower"]) & numpy.array(events.ggMass < options["diphotons"]["mgg_upper"])
    else:
        sideband_low = numpy.array(events.ggMass > options["diphotons"]["mgg_lower"]) & numpy.array(events.ggMass < options["diphotons"]["mgg_sideband_lower"])
        sideband_high = numpy.array(events.ggMass > options["diphotons"]["mgg_sideband_upper"]) & numpy.array(events.ggMass < options["diphotons"]["mgg_upper"])
        mgg_mask = sideband_low | sideband_high

    ### pt/mgg cuts ###
    lead_pt_mgg_requirement = (selected_photons.pt / events.ggMass) > options["photons"]["lead_pt_mgg_cut"]
    sublead_pt_mgg_requirement = (selected_photons.pt / events.ggMass) > options["photons"]["sublead_pt_mgg_cut"]

    lead_pt_mgg_cut = awkward.num(selected_photons[lead_pt_mgg_requirement]) >= 1 # at least 1 photon passing lead requirement
    sublead_pt_mgg_cut = awkward.num(selected_photons[sublead_pt_mgg_requirement]) >= 2 # at least 2 photon passing sublead requirement
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
