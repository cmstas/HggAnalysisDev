import awkward as ak
import numpy as np

def set_genZ(events, genBranches, selection_options, debug):
    if genBranches is None:
        events["genZ_decayMode"] = ak.from_numpy(-1 * np.ones(len(events)))
    else:
        electron_idxs = abs(genBranches.pdgId) == 11
        muon_idxs = abs(genBranches.pdgId) == 13
        tau_idxs = abs(genBranches.pdgId) == 15

        motherOfElectrons = genBranches.genPartIdxMother[electron_idxs]
        motherOfMuons = genBranches.genPartIdxMother[muon_idxs]
        motherOfTaus = genBranches.genPartIdxMother[tau_idxs]

        ZToEleEvents = ak.sum((genBranches.pdgId[motherOfElectrons] == 23), axis=1) > 0 
        ZToMuEvents = ak.sum((genBranches.pdgId[motherOfMuons] == 23), axis=1) > 0 
        ZToTauEvents = ak.sum((genBranches.pdgId[motherOfTaus] == 23), axis=1) > 0 
        
        # W decay dudes
        WToEEvents = ak.sum((abs(genBranches.pdgId[motherOfElectrons]) == 24), axis = 1) > 0
        WToMuEvents = ak.sum((abs(genBranches.pdgId[motherOfMuons]) == 24), axis = 1) > 0
        WToTauEvents = ak.sum((abs(genBranches.pdgId[motherOfTaus]) == 24), axis = 1) > 0
        
        events["genZ_decayMode"] = ak.from_numpy(np.zeros(len(events))) + 1 * ZToEleEvents + 2 * ZToMuEvents + 3 * ZToTauEvents + 4 * WToEEvents + 5 * WToMuEvents + 6 * WToTauEvents
        events["tau_motherID"] = ak.fill_none(ak.firsts(genBranches.pdgId[motherOfTaus]),0)
    return events
