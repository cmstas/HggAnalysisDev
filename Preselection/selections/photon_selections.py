import awkward
import numpy

import selections.selection_utils as utils

def diphoton_preselection(events, debug):
    cut_diagnostics = utils.CutDiagnostics(n_events_initial = len(events), debug = debug, cut_set = "[photon_selections.py : diphoton_preselection]")
    
    # mgg cut
    mgg_mask = numpy.array(events.ggMass > 100) & numpy.array(events.ggMass < 180)
    events = events[mgg_mask]
    cut_diagnostics.add_cut(len(events), cut_name = "mgg cut")

    # pt/mgg cuts
    pt_mgg_cut1 = (events.Photon_pt / events.ggMass) > 0.33
    pt_mgg_cut2 = (events.Photon_pt / events.ggMass) > 0.25

    n_pho1 = awkward.num(events.Photon_pt[pt_mgg_cut1])
    n_pho2 = awkward.num(events.Photon_pt[pt_mgg_cut2])
    pt_mgg_mask = numpy.array(n_pho1 >= 1) & numpy.array(n_pho2 >= 2)

    events = events[pt_mgg_mask]
    cut_diagnostics.add_cut(len(events), cut_name = "pt/mgg cut")

    # pho id mva cuts
    pho_idmva_cut = events.Photon_mvaID > -0.7
    n_pho = awkward.num(events.Photon_pt[pho_idmva_cut])
    pho_idmva_mask = numpy.array(n_pho >= 2)

    events = events[pho_idmva_mask]
    cut_diagnostics.add_cut(len(events), cut_name = "photon id mva cut")

    # electron veto cuts
    eveto_cut = events.Photon_electronVeto == 1
    n_pho = awkward.num(events.Photon_pt[eveto_cut])
    eveto_mask = numpy.array(n_pho >= 2)
    events = events[eveto_mask]
    cut_diagnostics.add_cut(len(events), cut_name = "electron veto cut")

    return events

def set_photons(events, debug):
    """
    Creates branches for photon-related variables
    """

    # Identify photons associated to diphoton pair
    pho1_idx = events.gHidx[:,0]
    pho2_idx = events.gHidx[:,1]

    #pho1_idx = numpy.array(events.gHidx[:,0]).reshape((-1,1))
    #pho2_idx = numpy.array(events.gHidx[:,1]).reshape((-1,1))


    #pick_lead_as1 = events.Photon_pt[pho1_idx] > events.Photon_pt[pho2_idx]
    #pick_sublead_as1 = events.Photon_pt[pho1_idx] < events.Photon_pt[pho2_idx]
    #lead_idx = numpy.where(pick_lead_as1, pho1_idx, pho2_idx)
    #sublead_idx = numpy.where(pick_sublead_as1, pho1_idx, pho2_idx)

    lead_idx = pho1_idx # FIXME: need to actually make these correspond to lead/sublead
    sublead_idx = pho2_idx

    events["lead_pho_ptmgg"] = events.Photon_pt[lead_idx] / events.ggMass
    events["sublead_pho_ptmgg"] = events.Photon_pt[sublead_idx] / events.ggMass

    return events
