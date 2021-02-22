import awkward
import numpy
import numba
import time

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

    idmva_cut = photons.mvaID > options["photons"]["idmva_cut"]
    eveto_cut = photons.electronVeto >= options["photons"]["eveto_cut"]

    r9_cut = photons.r9 > options["photons"]["r9"]

    iso_cut1 = photons.chargedHadronIso < options["photons"]["ch_iso"]
    iso_cut2 = photons.chargedHadronIso / photons.pt < options["photons"]["ch_reliso"]
    iso_cut = iso_cut1 | iso_cut2

    hoe_cut = photons.hoe < options["photons"]["hoe"]

    hlt_cut = photon_hlt_cuts(events, photons, debug)

    photon_cut = pt_cut & eta_cut & idmva_cut & eveto_cut & r9_cut & iso_cut & hoe_cut & hlt_cut

    cuts = [pt_cut, eta_cut, idmva_cut, eveto_cut, r9_cut, iso_cut, hoe_cut, hlt_cut, photon_cut]
    names = ["pt", "eta", "idmva", "eveto", "r9", "iso", "hoe", "hlt", "all"]
    cut_diagnostics.add_cuts(cuts, names)

    return photon_cut


def photon_hlt_cuts(events, photons, debug):
    start = time.time()
    nEvents = len(photons)
    nPhotons = numpy.array(awkward.num(photons), numpy.int64)

    mask_offsets = numpy.zeros(nEvents+1, numpy.int64)
    mask_contents = numpy.empty(awkward.sum(nPhotons), numpy.bool)

    rho = events.fixedGridRhoAll
    mask_offsets, mask_contents = apply_photon_hlt_cuts(photons, rho, nEvents, nPhotons, mask_offsets, mask_contents, debug)
    
    mask = awkward.Array(awkward.layout.ListOffsetArray64(awkward.layout.Index64(mask_offsets), awkward.layout.NumpyArray(mask_contents)))

    elapsed_time = time.time() - start
    print("[photon_selections.py] PERFORMANCE: time to execute photon HLT cuts: %.6f" % (elapsed_time))
    return mask

@numba.njit
def apply_photon_hlt_cuts(photons, rho, nEvents, nPhotons, mask_offsets, mask_contents, debug):
    """
    Mimic HLT Trigger
    """

    for i in range(nEvents):
        mask_offsets[i+1] = mask_offsets[i] + nPhotons[i]
        for j in range(nPhotons[i]):
            mask_contents[mask_offsets[i] + j] = False

            eb = photons[i][j].isScEtaEB
            ee = photons[i][j].isScEtaEE
            r9 = photons[i][j].r9
            eta = photons[i][j].eta
            iso = photons[i][j].photonIso - (photon_eff_area(abs(eta)) * rho[i])

            if eb:
                if r9 <= 0.85 and r9 > 0.8: # eb low r9
                    if iso >= 4.0:
                        continue
                    if photons[i][j].trkSumPtHollowConeDR03 >= 6.0:
                        continue
                    if photons[i][j].sieie >= 0.015:
                        continue
            elif ee:
                if r9 <= 0.9 and r9 > 0.8: # ee low r9
                    if iso >= 4.0:
                        continue
                    if photons[i][j].trkSumPtHollowConeDR03 >= 6.0:
                        continue
                    if photons[i][j].sieie >= 0.035:
                        continue
            
            else:
                continue

            mask_contents[mask_offsets[i] + j] = True

    return mask_offsets, mask_contents

@numba.njit
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
