import awkward as ak

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

        ZToEleEvents = ak.sum((genBranches.pdgId[motherOfElectrons] == 23), axis=1) >= 2
        ZToMuEvents = ak.sum((genBranches.pdgId[motherOfMuons] == 23), axis=1) >= 2
        ZToTauEvents = ak.sum((genBranches.pdgId[motherOfTaus] == 23), axis=1) >= 2

        events["genZ_decayMode"] = 1 * ZToEleEvents + 2 * ZToMuEvents + 3 * ZToTauEvents

    return events
