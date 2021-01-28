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


