import awkward
import numpy
import numba

import selections.selection_utils as utils
import selections.object_selections as object_selections
import selections.lepton_selections as lepton_selections
import selections.tau_selections as tau_selections
import selections.photon_selections as photon_selections
import selections.jet_selections as jet_selections
import selections.gen_selections as gen_selections
import selections.compound_selections as compound_selections

def ggTauTau_inclusive_preselection(events, photons, electrons, muons, taus, jets, dR, genPart, Category_pairsLoose, options, debug):
    """
    Performs inclusive ggTauTau preselection, requiring >=1 (leptons + tau_h).
    Assumes diphoton preselection has already been applied.
    Also calculates relevant event-level variables.
    """
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

    # only events with hadronic taus (no leptonic taus!!!!!!!!!!)
    atleast_one_had_tau_cut = (n_taus >= 1)
    # Require OS leptons/taus for events with 2 leptons/taus
    sum_charge = awkward.sum(selected_electrons.charge, axis=1) + awkward.sum(selected_muons.charge, axis=1) + awkward.sum(selected_taus.charge, axis=1)
    charge_cut = sum_charge == 0
    two_leptons = n_leptons_and_taus == 2
    not_two_leptons = n_leptons_and_taus != 2
    os_cut = (two_leptons & charge_cut) | not_two_leptons  # only require 2 OS leptons if there are ==2 leptons in the event

    # Select jets (don't cut on jet quantities for selection, but they will be useful for BDT training)
    selected_jets = jets[jet_selections.select_jets(events, photons, selected_electrons, selected_muons, selected_taus, jets, options, debug)]

    all_cuts = os_cut & atleast_one_had_tau_cut
    cut_diagnostics.add_cuts([atleast_one_had_tau_cut, os_cut, all_cuts], ["N_taus >= 1", "OS dileptons", "all"])

    # Keep only selected events
    selected_events = events[all_cuts]
    selected_photons = photons[all_cuts]
    selected_electrons = selected_electrons[all_cuts]
    selected_muons = selected_muons[all_cuts]
    selected_taus = selected_taus[all_cuts]
    selected_jets = selected_jets[all_cuts]
    dR = dR[all_cuts]

    # Calculate event-level variables
    selected_events = lepton_selections.set_electrons(selected_events, selected_electrons, debug)
    selected_events = lepton_selections.set_muons(selected_events, selected_muons, debug)
    selected_events = tau_selections.set_taus(selected_events, selected_taus, debug)
    selected_events = jet_selections.set_jets(selected_events, selected_jets, options, debug)
    if genPart is not None:
        genPart = genPart[all_cuts]
        selected_events = gen_selections.set_genZ(selected_events, genPart, options, debug)
    else:
        selected_events["genZ_decayMode"] = awkward.from_numpy(numpy.ones(len(selected_events)) * -1)
        selected_events["tau_motherID"] = awkward.from_numpy(numpy.ones(len(selected_events)) * -1)

    selected_events = compound_selections.compound_selections(selected_events, options, debug)
    return selected_events

def tth_leptonic_preselection(events, photons, electrons, muons, jets, options, debug):
    """
    Performs tth leptonic preselection, requiring >= 1 lepton and >= 1 jet
    Assumes diphoton preselection has already been applied.
    Also calculates relevant event-level variables.
    """

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

    # Keep only selected events
    selected_events = events[all_cuts]
    selected_photons = photons[all_cuts]
    selected_electrons = selected_electrons[all_cuts]
    selected_muons = selected_muons[all_cuts]
    selected_jets = selected_jets[all_cuts]

    # Calculate event-level variables
    selected_events = lepton_selections.set_electrons(selected_events, selected_electrons, debug)
    selected_events = lepton_selections.set_muons(selected_events, selected_muons, debug)
    selected_events = jet_selections.set_jets(selected_events, selected_jets, options, debug)

    return selected_events

def tth_hadronic_preselection(events, photons, electrons, muons, jets, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : tth_hadronic_preselection]")

    # Get number of electrons, muons

    selected_electrons = electrons[lepton_selections.select_electrons(events, photons, electrons, options, debug)]
    selected_muons = muons[lepton_selections.select_muons(events, photons, muons, options, debug)]

    n_electrons = awkward.num(selected_electrons)
    n_muons = awkward.num(selected_muons)
    n_leptons = n_electrons + n_muons

    # Get number of jets
    selected_jets = jets[jet_selections.select_jets(events, photons, selected_electrons, selected_muons, None, jets, options, debug)]
    n_jets = awkward.num(selected_jets)

    # Get number of b-jets
    selected_bjets = selected_jets[jet_selections.select_bjets(selected_jets, options, debug)]
    n_bjets = awkward.num(selected_bjets)

    lep_cut = n_leptons == 0
    jet_cut = n_jets >= 3
    bjet_cut = n_bjets >= 1

    all_cuts = lep_cut & jet_cut & bjet_cut
    cut_diagnostics.add_cuts([lep_cut, jet_cut, bjet_cut, all_cuts], ["N_leptons == 0", "N_jets >= 3", "N_bjets >= 1", "all"])

    # Keep only selected events
    selected_events = events[all_cuts]
    selected_photons = photons[all_cuts]
    selected_electrons = selected_electrons[all_cuts]
    selected_muons = selected_muons[all_cuts]
    selected_jets = selected_jets[all_cuts]

    # Calculate event-level variables
    selected_events = lepton_selections.set_electrons(selected_events, selected_electrons, debug)
    selected_events = lepton_selections.set_muons(selected_events, selected_muons, debug)
    selected_events = jet_selections.set_jets(selected_events, selected_jets, options, debug)

    return selected_events

def tth_inclusive_preselection(events, photons, electrons, muons, jets, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : tth_inclusive_preselection]")

    # Get number of electrons, muons

    selected_electrons = electrons[lepton_selections.select_electrons(events, photons, electrons, options, debug)]
    selected_muons = muons[lepton_selections.select_muons(events, photons, muons, options, debug)]

    n_electrons = awkward.num(selected_electrons)
    n_muons = awkward.num(selected_muons)
    n_leptons = n_electrons + n_muons

    # Get number of jets
    selected_jets = jets[jet_selections.select_jets(events, photons, selected_electrons, selected_muons, None, jets, options, debug)]
    n_jets = awkward.num(selected_jets)

    # Get number of b-jets
    selected_bjets = selected_jets[jet_selections.select_bjets(selected_jets, options, debug)]
    n_bjets = awkward.num(selected_bjets)

    lep_cut_leptonic = n_leptons >= 1
    jet_cut_leptonic = n_jets >= 1
    all_cuts_leptonic = lep_cut_leptonic & jet_cut_leptonic

    lep_cut_hadronic = n_leptons == 0
    jet_cut_hadronic = n_jets >= 3
    bjet_cut_hadronic = n_bjets >= 1
    all_cuts_hadronic = lep_cut_hadronic & jet_cut_hadronic & bjet_cut_hadronic

    all_cuts = all_cuts_leptonic | all_cuts_hadronic
    cut_diagnostics.add_cuts([lep_cut_leptonic, jet_cut_leptonic, all_cuts_leptonic, lep_cut_hadronic, jet_cut_hadronic, bjet_cut_hadronic, all_cuts_hadronic, all_cuts], ["N_leptons >= 1", "N_jets >= 1", "leptonic_presel", "N_leptons == 0", "N_jets >= 3", "N_bjets >= 1", "hadronic_presel", "all"])

    # Keep only selected events
    selected_events = events[all_cuts]
    selected_photons = photons[all_cuts]
    selected_electrons = selected_electrons[all_cuts]
    selected_muons = selected_muons[all_cuts]
    selected_jets = selected_jets[all_cuts]

    # Calculate event-level variables
    selected_events = lepton_selections.set_electrons(selected_events, selected_electrons, debug)
    selected_events = lepton_selections.set_muons(selected_events, selected_muons, debug)
    selected_events = jet_selections.set_jets(selected_events, selected_jets, options, debug)

    return selected_events


def ggbb_preselection(events, photons, electrons, muons, jets, fatjets, options, debug):
    cut_diagnostics = utils.CutDiagnostics(events = events, debug = debug, cut_set = "[analysis_selections.py : ggbb_preselection]")

    # Get number of electrons, muons

    selected_electrons = electrons[lepton_selections.select_electrons(events, photons, electrons, options, debug)]
    selected_muons = muons[lepton_selections.select_muons(events, photons, muons, options, debug)]

    n_electrons = awkward.num(selected_electrons)
    n_muons = awkward.num(selected_muons)
    n_leptons = n_electrons + n_muons

    # Get number of jets
    selected_jets = jets[jet_selections.select_jets(events, photons, selected_electrons, selected_muons, None, jets, options, debug)]
    n_jets = awkward.num(selected_jets)

    # Get number of b-jets
    selected_bjets = selected_jets[jet_selections.select_bjets(selected_jets, options, debug)]
    n_bjets = awkward.num(selected_bjets)

    # Get fat jets
    selected_fatjets = fatjets[jet_selections.select_fatjets(events, photons, fatjets, options, debug)]
    n_fatjets = awkward.num(selected_fatjets)

    lep_cut = n_leptons == 0
    if options["boosted"]:
        jet_cut = n_bjets < 2
        fatjet_cut = n_fatjets == 1
        all_cuts = lep_cut & jet_cut & fatjet_cut
        cut_diagnostics.add_cuts([lep_cut, jet_cut, fatjet_cut, all_cuts], ["N_leptons == 0", "N_b-jets < 2", "N_fatjets == 1", "all"])
    else:
        jet_cut = n_bjets == 2
        all_cuts = lep_cut & jet_cut
        cut_diagnostics.add_cuts([lep_cut, jet_cut, all_cuts], ["N_leptons == 0", "N_b-jets == 2", "all"])

    # Keep only selected events
    selected_events = events[all_cuts]
    selected_photons = photons[all_cuts]
    selected_jets = selected_jets[all_cuts]
    selected_fatjets = selected_fatjets[all_cuts]

    # Calculate event-level variables
    selected_events = jet_selections.set_jets(selected_events, selected_jets, options, debug)
    selected_events = jet_selections.set_fatjets(selected_events, selected_fatjets, options, debug)

    return selected_events
