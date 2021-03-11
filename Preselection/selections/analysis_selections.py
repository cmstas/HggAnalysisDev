import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections
import selections.lepton_selections as lepton_selections
import selections.tau_selections as tau_selections
import selections.photon_selections as photon_selections
import selections.jet_selections as jet_selections

def ggTauTau_inclusive_preselection(events, photons, electrons, muons, taus, dR, options, debug, genPart = None):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : ggTauTau_inclusive_preselection]")

    # Get number of electrons, muons, taus
    selected_electrons = electrons[lepton_selections.select_electrons(events, photons, electrons, options, debug)]
    selected_muons = muons[lepton_selections.select_muons(events, photons, muons, options, debug)]
    selected_taus = taus[tau_selections.select_taus(events, photons, selected_muons, selected_electrons, taus, options, debug)]

    n_electrons = awkward.num(selected_electrons)
    n_muons = awkward.num(selected_muons)
    n_taus = awkward.num(selected_taus)

    # Require >= 1 lep/tau
    n_leptons_and_taus = n_electrons + n_muons + n_taus
    lep_tau_cut = n_leptons_and_taus >= options["n_leptons_and_taus"]

    # Require OS leptons/taus for events with 2 leptons/taus
    sum_charge = awkward.sum(selected_electrons.charge, axis=1) + awkward.sum(selected_muons.charge, axis=1) + awkward.sum(selected_taus.charge, axis=1)
    charge_cut = sum_charge == 0
    two_leptons = n_leptons_and_taus == 2
    not_two_leptons = n_leptons_and_taus != 2
    os_cut = (two_leptons & charge_cut) | not_two_leptons # only require 2 OS leptons if there are ==2 leptons in the event

    all_cuts = lep_tau_cut & os_cut
    cut_diagnostics.add_cuts([lep_tau_cut, os_cut, all_cuts], ["N_leptons + N_taus >= 1", "OS dileptons", "all"])
    if genPart is not None:
        return events[all_cuts], photons[all_cuts], selected_electrons[all_cuts], selected_muons[all_cuts], selected_taus[all_cuts], dR[all_cuts], genPart[all_cuts]
    else:
         return events[all_cuts], photons[all_cuts], selected_electrons[all_cuts], selected_muons[all_cuts], selected_taus[all_cuts], dR[all_cuts]


def tth_leptonic_preselection(events, photons, electrons, muons, jets, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : tth_leptonic_preselection]")

    # Get number of electrons, muons

    selected_electrons = electrons[lepton_selections.select_electrons(events, photons, electrons, options, debug)]
    selected_muons = muons[lepton_selections.select_muons(events, photons, muons, options, debug)]

    n_electrons = awkward.num(selected_electrons)
    n_muons = awkward.num(selected_muons)
    n_leptons = n_electrons + n_muons

    # Get number of jets
    selected_jets = jets[jet_selections.select_jets(events, photons, selected_electrons, selected_muons, None, jets, options, debug)]
    n_jets = awkward.num(selected_jets)

    lep_cut = n_leptons >= 1
    jet_cut = n_jets >= 1

    all_cuts = lep_cut & jet_cut
    cut_diagnostics.add_cuts([lep_cut, jet_cut, all_cuts], ["N_leptons >= 1", "N_jets >= 1", "all"])

    return events[all_cuts], photons[all_cuts], selected_electrons[all_cuts], selected_muons[all_cuts], selected_jets[all_cuts]
