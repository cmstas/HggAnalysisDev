import awkward as ak

def set_genZ(events, selection_options, debug):
    electron_idxs = abs(events.GenPart_pdgId) == 11
    muon_idxs = abs(events.GenPart_pdgId) == 13
    tau_idxs = abs(events.GenPart_pdgId) == 15

    motherOfElectrons = events.GenPart_genPartIdxMother[electron_idxs]
    motherOfMuons = events.GenPart_genPartIdxMother[muon_idxs]
    motherOfTaus = events.GenPart_genPartIdxMother[tau_idxs]

    ZToEleEvents = ak.sum((events.GenPart_pdgId[motherOfElectrons] == 23), axis=1) >= 2
    ZToMuEvents = ak.sum((events.GenPart_pdgId[motherOfMuons] == 23), axis=1) >= 2
    ZToTauEvents = ak.sum((events.GenPart_pdgId[motherOfTaus] == 23), axis=1) >= 2

    events["genZ_decayMode"] = 1 * ZToEleEvents + 2 * ZToMuEvents + 3 * ZToTauEvents

    return events
