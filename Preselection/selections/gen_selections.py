import awkward as ak
import numpy
import selections.selection_utils as utils


def filter_genHbb(events, genparts, options, debug):
    if options["signal"]:
        mask_genB = abs(genparts.pdgId) == 5
        mIdx = genparts.genPartIdxMother
        mask_fromH = genparts.pdgId[mIdx] == 25
        genB_fromH = genparts[mask_genB & mask_fromH]

        dR_bb = object_selections.compute_deltaR(
            genB_fromH.phi[:, 0], genB_fromH.phi[:, 1], genB_fromH.eta[:, 0], genB_fromH.eta[:, 1])

        gen_cut = dR_bb <= 0.8
    else:
        gen_cut = events["event"]>0 #dummy filter
    return gen_cut

def set_genZ(events, genBranches, selection_options, debug):
    if genBranches is None:
        events["genZ_decayMode"] = ak.from_numpy(-1 * numpy.ones(len(events)))
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

        events["genZ_decayMode"] = ak.from_numpy(numpy.zeros(len(events))) + 1 * ZToEleEvents + 2 * ZToMuEvents + 3 * ZToTauEvents + 4 * WToEEvents + 5 * WToMuEvents + 6 * WToTauEvents
        events["tau_motherID"] = ak.fill_none(ak.firsts(genBranches.pdgId[motherOfTaus]),0)
    return events


def set_genInfo(events, genparts, selection_options, debug):
    if genparts is None:
        return events
    else:
        # All genParts saving 
        n_save = 60
        GenPart_pt_padded = utils.pad_awkward_array(genparts.pt, n_save, -9)
        GenPart_eta_padded = utils.pad_awkward_array(genparts.eta, n_save, -9)
        GenPart_phi_padded = utils.pad_awkward_array(genparts.phi, n_save, -9)
        GenPart_mass_padded = utils.pad_awkward_array(genparts.mass, n_save, -9)
        GenPart_pdgId_padded = utils.pad_awkward_array(genparts.pdgId, n_save, -9)
        GenPart_status_padded = utils.pad_awkward_array(genparts.status, n_save, -9)
        GenPart_statusFlags_padded = utils.pad_awkward_array(genparts.statusFlags, n_save, -9)
        GenPart_genPartIdxMother_padded = utils.pad_awkward_array(genparts.genPartIdxMother, n_save, -9)

        for i in range(n_save):
            events["genPart%s_pt" % str(i+1)] = GenPart_pt_padded[:, i]
            events["genPart%s_eta" % str(i+1)] = GenPart_eta_padded[:, i]
            events["genPart%s_phi" % str(i+1)] = GenPart_phi_padded[:, i]
            events["genPart%s_mass" % str(i+1)] = GenPart_mass_padded[:, i]
            events["genPart%s_pdgId" % str(i+1)] = GenPart_pdgId_padded[:, i]
            events["genPart%s_status" % str(i+1)] = GenPart_status_padded[:, i]
            events["genPart%s_statusFlags" % str(i+1)] = GenPart_statusFlags_padded[:, i]
            events["genPart%s_genPartIdxMother" % str(i+1)] = GenPart_genPartIdxMother_padded[:, i]

    return events
