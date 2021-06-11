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


def select_photons_full(events, photons, options, debug):
    # pt
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = photons, cut_set = "[photon_selections.py : select_photons_full]", debug = debug)

    pt_cut = photons.pt > options["pt"]

    # eta
    eta_cut1 = abs(photons.eta) < options["eta"]
    eta_cut2 = abs(photons.eta) < options["transition_region_eta"][0]
    eta_cut3 = abs(photons.eta) > options["transition_region_eta"][1]
    eta_cut = eta_cut1 & (eta_cut2 | eta_cut3) 

    # electron veto
    e_veto_cut = photons.electronVeto > options["e_veto"]

    use_central_nano = options["use_central_nano"] # indicates whether we are using central nanoAOD (with some branches that are necessary for full diphoton preselection missing) or custom nanoAOD (with these branches added)

    # r9/isolation cut
    r9_cut = photons.r9 > options["r9"]

    if not use_central_nano:
        charged_iso_cut = photons.chargedHadronIso < options["charged_iso"]
        charged_rel_iso_cut = (photons.chargedHadronIso / photons.pt) < options["charged_rel_iso"]

    else:
        charged_iso_cut = (photons.pfRelIso03_chg * photons.pt) < options["charged_iso"]
        charged_rel_iso_cut = photons.pfRelIso03_chg < options["charged_rel_iso"]

    r9_iso_cut = r9_cut | charged_iso_cut | charged_rel_iso_cut

    # hadronic over em energy cut
    hoe_cut = photons.hoe < options["hoe"]

    # hlt-mimicking cuts
    photons_eb_high_r9 = photons.isScEtaEB & (photons.r9 > options["hlt"]["eb_high_r9"]["r9"])
    photons_eb_low_r9 = photons.isScEtaEB & (photons.r9 > options["hlt"]["eb_low_r9"]["r9"]) & (photons.r9 < options["hlt"]["eb_high_r9"]["r9"])

    photons_ee_high_r9 = photons.isScEtaEE & (photons.r9 > options["hlt"]["ee_high_r9"]["r9"])
    photons_ee_low_r9 = photons.isScEtaEE & (photons.r9 > options["hlt"]["ee_low_r9"]["r9"]) & (photons.r9 < options["hlt"]["ee_high_r9"]["r9"])

    if not use_central_nano:
        eb_low_r9_track_pt_cut = photons.trkSumPtHollowConeDR03 < options["hlt"]["eb_low_r9"]["track_sum_pt"]
        ee_low_r9_track_pt_cut = photons.trkSumPtHollowConeDR03 < options["hlt"]["ee_low_r9"]["track_sum_pt"]

    else:
        eb_low_r9_track_pt_cut = photons.pt > 0
        ee_low_r9_track_pt_cut = photons.pt > 0

    eb_low_r9_sigma_ieie_cut = photons.sieie < options["hlt"]["eb_low_r9"]["sigma_ieie"]
    ee_low_r9_sigma_ieie_cut = photons.sieie < options["hlt"]["eb_low_r9"]["sigma_ieie"]

    low_eta = abs(photons.eta) < options["hlt"]["eta_rho_corr"]

    if not use_central_nano:
        eb_low_r9_pho_iso_low_eta_cut = low_eta & (photons.photonIso * options["hlt"]["low_eta_rho_corr"] < options["hlt"]["eb_low_r9"]["pho_iso"])
        eb_low_r9_pho_iso_high_eta_cut = ~low_eta & (photons.photonIso * options["hlt"]["high_eta_rho_corr"] < options["hlt"]["eb_low_r9"]["pho_iso"])
    else:
        eb_low_r9_pho_iso_low_eta_cut = low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["low_eta_rho_corr"]) < options["hlt"]["eb_low_r9"]["pho_iso"])
        eb_low_r9_pho_iso_high_eta_cut = ~low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["high_eta_rho_corr"]) < options["hlt"]["eb_low_r9"]["pho_iso"])

    eb_low_r9_pho_iso_cut = eb_low_r9_pho_iso_low_eta_cut | eb_low_r9_pho_iso_high_eta_cut

    if not use_central_nano:
        ee_low_r9_pho_iso_low_eta_cut = low_eta & (photons.photonIso * options["hlt"]["low_eta_rho_corr"] < options["hlt"]["ee_low_r9"]["pho_iso"])
        ee_low_r9_pho_iso_high_eta_cut = ~low_eta & (photons.photonIso * options["hlt"]["high_eta_rho_corr"] < options["hlt"]["ee_low_r9"]["pho_iso"])
    else:
        ee_low_r9_pho_iso_low_eta_cut = low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["low_eta_rho_corr"]) < options["hlt"]["ee_low_r9"]["pho_iso"])
        ee_low_r9_pho_iso_high_eta_cut = ~low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["high_eta_rho_corr"]) < options["hlt"]["ee_low_r9"]["pho_iso"])

    ee_low_r9_pho_iso_cut = ee_low_r9_pho_iso_low_eta_cut | ee_low_r9_pho_iso_high_eta_cut

    hlt_cut = photons.pt < 0 # initialize to all False
    hlt_cut = hlt_cut | photons_eb_high_r9
    hlt_cut = hlt_cut | (photons_eb_low_r9 & eb_low_r9_track_pt_cut & eb_low_r9_sigma_ieie_cut & eb_low_r9_pho_iso_cut)
    hlt_cut = hlt_cut | photons_ee_high_r9
    hlt_cut = hlt_cut | (photons_ee_low_r9 & ee_low_r9_track_pt_cut & ee_low_r9_sigma_ieie_cut & ee_low_r9_pho_iso_cut)

    idmva_cut = photons.mvaID > options["idmva_cut"]
    
    all_cuts = pt_cut & eta_cut & e_veto_cut & r9_iso_cut & hoe_cut & hlt_cut & idmva_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, e_veto_cut, r9_iso_cut, hoe_cut, hlt_cut, idmva_cut, all_cuts], ["pt", "eta", "e veto", "r9/iso", "hoe", "hlt", "idmva", "all"]) 
    #cut_diagnostics.add_cuts([pt_cut, eta_cut, idmva_cut, eveto_cut, photon_cut], ["pt > 25", "|eta| < 2.5", "idmva", "eveto", "all"])

    return all_cuts


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
