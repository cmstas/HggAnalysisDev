import awkward
import numpy
import numba
import vector

import selections.selection_utils as utils
from selections import photon_selections, object_selections, awkward_utils

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


@numba.njit
def produce_diphotons(photons, n_photons, lead_pt_cut):
    n_events = len(photons)

    diphotons_offsets = numpy.zeros(n_events + 1, numpy.int64)
    diphotons_contents = []
    lead_photons_idx = []
    sublead_photons_idx = []

    # Loop through events and select diphoton pairs
    for i in range(n_events):
        #diphotons_evt = []
        n_diphotons_event = 0
        # Enumerate photon pairs
        if n_photons[i] >= 2: # only try if there are at least 2 photons
            for j in range(n_photons[i]):
                for k in range(j, n_photons[i]):
                    # Choose who is the leading photon
                    lead_idx = j if photons[i][j].pt > photons[i][k].pt else k
                    sublead_idx = k if photons[i][j].pt > photons[i][k].pt else j

                    lead_photon = photons[i][lead_idx]
                    sublead_photon = photons[i][sublead_idx]

                    # Lead photon must satisfy lead pt cut
                    if lead_photon.pt < lead_pt_cut:
                        continue

                    # Quickly calculate mass before calculating whole diphoton four vector
                    mass = numpy.sqrt(2 * lead_photon.pt * sublead_photon.pt * (numpy.cosh(lead_photon.eta - sublead_photon.eta) - numpy.cos(lead_photon.phi - sublead_photon.phi)))

                    if mass < 100 or mass > 180:
                        continue

                    # Construct four vectors
                    lead_photon_vec = vector.obj(
                            pt = lead_photon.pt,
                            eta = lead_photon.eta,
                            phi = lead_photon.phi,
                            mass = lead_photon.mass
                    )
                    sublead_photon_vec = vector.obj(
                            pt = sublead_photon.pt,
                            eta = sublead_photon.eta,
                            phi = sublead_photon.phi,
                            mass = sublead_photon.mass
                    )

                    # Check for two photons on top of each other (not sure why this happens)
                    dR = lead_photon_vec.deltaR(sublead_photon_vec)
                    if dR < 0.2:
                        continue

                    diphoton = vector.obj(px = 0., py = 0., pz = 0., E = 0.) # IMPORTANT NOTE: you need to initialize this to an empty vector first. Otherwise, you will get ZeroDivisionError exceptions for like 1 out of a million events (seemingly only with numba). 
                    diphoton = diphoton + lead_photon_vec + sublead_photon_vec

                    if numpy.isnan(diphoton.pt) or numpy.isnan(diphoton.mass) or numpy.isnan(diphoton.eta) or numpy.isnan(diphoton.phi):
                        continue 

                    # Enforce diphoton mass requirements
                    if diphoton.mass < 100 or diphoton.mass > 180:
                        continue

                    # This diphoton candidate passes
                    n_diphotons_event += 1

                    
                    diphotons_contents.append([
                        diphoton.pt,
                        diphoton.eta,
                        diphoton.phi,
                        diphoton.mass
                    ])

                    lead_photons_idx.append(lead_idx)
                    sublead_photons_idx.append(sublead_idx)

        diphotons_offsets[i+1] = diphotons_offsets[i] + n_diphotons_event

    return diphotons_offsets, numpy.array(diphotons_contents), numpy.array(lead_photons_idx), numpy.array(sublead_photons_idx)


def diphoton_preselection_full(events, photons, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[diphoton_selections.py : diphoton_preselection]")

    n_pho_cut = awkward.num(photons) >= 2
    events = events[n_pho_cut]
    photons = photons[n_pho_cut]

    cut_diagnostics.add_cuts([n_pho_cut], ["n_photons >= 2"])

    n_photons = awkward.num(photons)
    lead_pt_cut = options["diphotons"]["lead_pt"]

    diphoton_offsets, diphoton_contents, lead_photon_idx, sublead_photon_idx = produce_diphotons(photons, n_photons, lead_pt_cut)

    # Zip diphotons into events array as records
    diphotons = {}
    diphotons["p4"] = awkward_utils.create_four_vectors(events, diphoton_offsets, diphoton_contents)
    #awkward_utils.create_record(events, diphotons, "Diphoton") 
    awkward_utils.add_field(events, "Diphoton", diphotons)

    lead_photon_idx = awkward_utils.construct_jagged_array(diphoton_offsets, lead_photon_idx)
    sublead_photon_idx = awkward_utils.construct_jagged_array(diphoton_offsets, sublead_photon_idx)

    # Zip lead/sublead photons into events.Diphoton as sub-records
    lead_photons = {}
    sublead_photons = {}
    for field in photons.fields:
        lead_photons[field] = photons[lead_photon_idx][field]
        sublead_photons[field] = photons[sublead_photon_idx][field]
    awkward_utils.add_field(events, ("Diphoton", "LeadPhoton"), lead_photons)
    awkward_utils.add_field(events, ("Diphoton", "SubleadPhoton"), sublead_photons)

    # Select events with at least 1 diphoton candidate
    dipho_presel_cut = awkward.num(events.Diphoton) >= 1

    if options["data"]:
        if options["year"] == 2016:
            trigger_cut = events.HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90 == True
        elif options["year"] == 2017 or options["year"] == 2018:
            trigger_cut = events.HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90 == True
    else:
        trigger_cut = events.MET_pt > 0 # dummy cut
 

    dipho_presel_cut = dipho_presel_cut & trigger_cut
    selected_events = events[dipho_presel_cut]
    selected_photons = photons[dipho_presel_cut]

    selected_events["gg_mass"] = selected_events.Diphoton.mass[:,0]
    selected_events["gg_pt"] = selected_events.Diphoton.pt[:,0]
    selected_events["gg_eta"] = selected_events.Diphoton.eta[:,0]
    selected_events["gg_phi"] = selected_events.Diphoton.phi[:,0]

    ### mgg cut ###
    resonant = options["resonant"]
    if resonant:
        mgg_mask = numpy.array(selected_events.gg_mass > options["diphotons"]["mgg_lower"]) & numpy.array(selected_events.gg_mass < options["diphotons"]["mgg_upper"])
    else:
        sideband_low = numpy.array(selected_events.gg_mass > options["diphotons"]["mgg_lower"]) & numpy.array(selected_events.gg_mass < options["diphotons"]["mgg_sideband_lower"])
        sideband_high = numpy.array(selected_events.gg_mass > options["diphotons"]["mgg_sideband_upper"]) & numpy.array(selected_events.gg_mass < options["diphotons"]["mgg_upper"])
        mgg_mask = sideband_low | sideband_high

    lead_pt_mgg_cut = selected_photons.pt[:,0] / selected_events.gg_mass > options["photons"]["lead_pt_mgg_cut"]
    sublead_pt_mgg_cut = selected_photons.pt[:,1] / selected_events.gg_mass > options["photons"]["sublead_pt_mgg_cut"]
    pt_mgg_cut = lead_pt_mgg_cut & sublead_pt_mgg_cut

    dipho_presel_cut = mgg_mask & pt_mgg_cut 

    selected_events = selected_events[dipho_presel_cut]
    selected_photons = selected_photons[dipho_presel_cut]

    selected_events = photon_selections.set_photons(selected_events, selected_photons, debug)
    selected_events = set_diphotons(selected_events, selected_photons, debug)

    return selected_events, selected_photons


def set_diphotons(events, selected_photons, debug):
    events["diphoton_pt_mgg"] = events["gg_pt"] / events["gg_mass"]
    events["diphoton_rapidity"] = events["gg_eta"]  # just using pseudorapidity, shouldn't be a big difference
    events["diphoton_delta_R"] = object_selections.compute_deltaR(
        selected_photons.phi[:,0],
        selected_photons.phi[:,1],
        selected_photons.eta[:,0],
        selected_photons.eta[:,1]
    )
    return events
