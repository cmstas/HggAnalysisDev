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

    selected_photons = photons[photon_selections.select_photons_full(events, photons, options, debug)]

    events, selected_photons = select_mgg_candidates(events, selected_photons, options, debug)
    return events, selected_photons


    #n_photon_cut = awkward.num(selected_photons) == 2
    #all_cuts = n_photon_cut
    #cut_diagnostics.add_cuts([n_photon_cut, all_cuts], ["n photons == 2", "all"])
    return events[all_cuts], photons[all_cuts]

def select_mgg_candidates(events, photons, options, debug):
    nEvents = len(photons)
    nPhotons = numpy.array(awkward.num(photons), numpy.int64)
    event_cut = events.MET_pt < 0 # dummy all false selection 

    mask_offsets = numpy.zeros(nEvents+1, numpy.int64)
    mask_contents = numpy.empty(awkward.sum(nPhotons), numpy.bool)

    event_cut, mask_offsets, mask_contents, mgg = apply_select_mgg_candidates(events, photons, nEvents, nPhotons, event_cut, mask_offsets, mask_contents)

    mask = awkward.Array(awkward.layout.ListOffsetArray64(awkward.layout.Index64(mask_offsets), awkward.layout.NumpyArray(mask_contents)))
    photons = photons[mask]
    events = events[event_cut]
    photons = photons[event_cut]
    events["mgg"] = mgg

    return events, photons

@numba.njit
def apply_select_mgg_candidates(events, photons, nEvents, nPhotons, event_cut, mask_offsets, mask_contents):

    selected_mgg = []
    for i in range(nEvents):
        mask_offsets[i+1] = mask_offsets[i] + nPhotons[i]

        # Consider all m_gg pairs
        m_gg_candidate = [0, 0, -1, -1]
        
        if nPhotons[i] < 2:
            continue

        for j in range(nPhotons[i]):
            mask_contents[mask_offsets[i] + j] = False
            for k in range(j, nPhotons[i]):
                mgg = calculate_mgg(
                    photons[i][j].pt, photons[i][j].eta, photons[i][j].phi,
                    photons[i][k].pt, photons[i][k].eta, photons[i][k].phi
                )
                if mgg < 100 or mgg > 180:
                    continue
                sum_pt = photons[i][j].pt + photons[i][k].pt
                if sum_pt > m_gg_candidates[1]:
                    m_gg_candidate = [mgg, sum_pt, j, k]

                event_cut[i] = True

        if m_gg_candidate[2] > -1:
            idx1 = m_gg_candidate[2]
            idx2 = m_gg_candidate[3]
            mask_contents[mask_offsets[i] + idx1] = True
            mask_contents[mask_offsets[i] + idx2] = True
            selected_mgg.append(m_gg_candidate)

    return event_cut, mask_offsets, mask_contents, selected_mgg[:,0]

@numba.njit
def calculate_mgg(pt1, eta1, phi1, pt2, eta2, phi2):
    return numpy.sqrt(2 * pt1 * pt2 * (numpy.cosh(eta1 - eta2) - numpy.cos(phi1 - phi2)))


