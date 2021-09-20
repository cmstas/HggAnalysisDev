import awkward
import numpy
import numba 

import selections.selection_utils as utils
import selections.object_selections as object_selections

def select_jets(events, photons, electrons, muons, taus, jets, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = jets, cut_set = "[jet_selections.py : select_jets]", debug = debug)

    pt_cut = jets.pt > options["jets"]["pt"]
    eta_cut = abs(jets.eta) < options["jets"]["eta"]

    dR_pho_cut = object_selections.select_deltaR(events, jets, photons, options["jets"]["dR_pho"], debug)
    dR_ele_cut = object_selections.select_deltaR(events, jets, electrons, options["jets"]["dR_lep"], debug)
    dR_muon_cut = object_selections.select_deltaR(events, jets, muons, options["jets"]["dR_lep"], debug)

    if taus is not None:
        dR_tau_cut = object_selections.select_deltaR(events, jets, taus, options["jets"]["dR_tau"], debug)
    else:
        dR_tau_cut = object_selections.select_deltaR(events, jets, photons, 0.0, debug) # dummy cut of all True

    id_cut = jet_id(jets, options)

    jet_cut = pt_cut & eta_cut & dR_pho_cut & dR_ele_cut & dR_muon_cut & dR_tau_cut & id_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, dR_pho_cut, dR_ele_cut, dR_muon_cut, dR_tau_cut, id_cut, jet_cut], ["pt > 25", "|eta| < 2.4", "dR_photons", "dR_electrons", "dR_muons", "dR_taus", "loose jet ID", "all"])
    
    return jet_cut



DEEPCSV_THRESHOLDS = {
    "2016" : {
        "loose" : 0.0614,
        "medium" : 0.3093,
        "tight" : 0.7221
    },
    "2017" : {
        "loose" : 0.0521,
        "medium" : 0.3033,
        "tight" : 0.7489
    },
    "2018" : {
        "loose" : 0.0494,
        "medium" : 0.2770,
        "tight" : 0.7264
    }
}

def select_bjets(jets, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = jets, cut_set = "[jet_selections.py : select_bjets]", debug = debug)

    bDisc_value = DEEPCSV_THRESHOLDS[str(options["year"])][options["jets"]["b_tag_thresh"]]
    bDisc_cut = jets.btagDeepFlavB > bDisc_value 

    cut_diagnostics.add_cuts([bDisc_cut], ["b-tag score >= %.3f" % bDisc_value]) 

    return bDisc_cut

def select_fatjets(events, photons, fatjets, options, debug):
    cut_diagnostics = utils.ObjectCutDiagnostics(objects = fatjets, cut_set = "[jet_selections.py : select_fatjets]", debug = debug)

    pt_cut = fatjets.pt > options["fatjets"]["pt"]
    eta_cut = abs(fatjets.eta) < options["fatjets"]["eta"]
    
    dR_pho_cut = object_selections.select_deltaR(events, fatjets, photons, options["fatjets"]["dR_pho"], debug)

    jet_cut = pt_cut & eta_cut & dR_pho_cut

    cut_diagnostics.add_cuts([pt_cut, eta_cut, dR_pho_cut, jet_cut], ["pt > %.1f" % options["fatjets"]["pt"], "eta < %.2f" % options["fatjets"]["eta"], "dR_photons", "all"])

    return jet_cut

def jet_id(jets, options):
    """
    Loose jet ID taken from flashgg: https://github.com/cms-analysis/flashgg/blob/dd6661a55448c403b46d1155510c67a313cd44a8/DataFormats/src/Jet.cc#L140-L155
    """
    nemf_cut = jets.neEmEF < 0.99
    nh_cut = jets.neHEF < 0.99
    chf_cut = jets.chHEF > 0
    chemf_cut = jets.chEmEF < 0.99
    n_constituent_cut = jets.nConstituents > 1

    id_cut = nemf_cut & nh_cut & chf_cut & chemf_cut & n_constituent_cut
    return id_cut

def set_fatjets(events, fatjets, genparts, options, debug):
    n_fatjets = awkward.num(fatjets)
    events["n_fatjets"] = n_fatjets
    n_save = 3  # with n_save==1 I guess padding is useless
    if options["signal"] and genparts is not None:
        # TODO here if I am running on signal samples do a gen matching (throwing away all but the one fatjet from the higgs)
        mask_genB = abs(genparts.pdgId) == 5
        mIdx = genparts.genPartIdxMother
        mask_fromH = genparts.pdgId[mIdx] == 25
        genB_fromH = genparts[mask_genB & mask_fromH]
        HbbIdx = genB_fromH.genPartIdxMother[:,0]

        Hbb_Pt = object_selections.getGenPartPtFromIdx(genparts,HbbIdx) 
        Hbb_Eta = object_selections.getGenPartEtaFromIdx(genparts,HbbIdx) 
        Hbb_Phi = object_selections.getGenPartPhiFromIdx(genparts,HbbIdx) 
        dR_bb = object_selections.compute_deltaR(genB_fromH.phi[:,0], genB_fromH.phi[:,1], genB_fromH.eta[:,0], genB_fromH.eta[:,1])
    
        # matching fatjet to Hbb: #TODO cut also on bbDr
        match_mask = object_selections.mask_nearest(Hbb_Eta,Hbb_Phi,fatjets.eta,fatjets.phi,threshold=0.4)
        matched_fatjet = fatjets[match_mask]   

        fatjet_pt_padded = utils.pad_awkward_array(matched_fatjet.pt, n_save, -9)
        fatjet_eta_padded = utils.pad_awkward_array(matched_fatjet.eta, n_save, -9)
        fatjet_phi_padded = utils.pad_awkward_array(matched_fatjet.phi, n_save, -9)
        fatjet_mass_padded = utils.pad_awkward_array(matched_fatjet.mass, n_save, -9)
        fatjet_msoftdrop_padded = utils.pad_awkward_array(matched_fatjet.msoftdrop, n_save, -9)
        fatjet_btag_padded = utils.pad_awkward_array(matched_fatjet.btagDDBvL_noMD, n_save, -9)
        fatjet_deepbtag_md_padded = utils.pad_awkward_array(matched_fatjet.deepTagMD_HbbvsQCD, n_save, -9)

        if hasattr(matched_fatjet,"particleNetMD_Xqq"):
            fatjet_PNet_Xqq_padded = utils.pad_awkward_array(matched_fatjet.particleNetMD_Xqq, n_save, -9)
            fatjet_PNet_Xcc_padded = utils.pad_awkward_array(matched_fatjet.particleNetMD_Xcc, n_save, -9)
            fatjet_PNet_Xbb_padded = utils.pad_awkward_array(matched_fatjet.particleNetMD_Xbb, n_save, -9)
            fatjet_PNet_XQCD_padded = utils.pad_awkward_array(matched_fatjet.particleNetMD_QCD, n_save, -9)

        events["Hbb_pt"] = Hbb_Pt
        events["Hbb_eta"] = Hbb_Eta
        events["Hbb_phi"] = Hbb_Phi
        events["genBBfromH_delta_R"] = dR_bb

    else :  
        
        fatjet_pt_padded = utils.pad_awkward_array(fatjets.pt, n_save, -9)
        fatjet_eta_padded = utils.pad_awkward_array(fatjets.eta, n_save, -9)
        fatjet_phi_padded = utils.pad_awkward_array(fatjets.phi, n_save, -9)
        fatjet_mass_padded = utils.pad_awkward_array(fatjets.mass, n_save, -9)
        fatjet_msoftdrop_padded = utils.pad_awkward_array(fatjets.msoftdrop, n_save, -9)
        fatjet_btag_padded = utils.pad_awkward_array(fatjets.btagDDBvL_noMD, n_save, -9)
        fatjet_deepbtag_md_padded = utils.pad_awkward_array(fatjets.deepTagMD_HbbvsQCD, n_save, -9)
    
        if hasattr(fatjets,"particleNetMD_Xqq"):
            fatjet_PNet_Xqq_padded = utils.pad_awkward_array(fatjets.particleNetMD_Xqq, n_save, -9)
            fatjet_PNet_Xcc_padded = utils.pad_awkward_array(fatjets.particleNetMD_Xcc, n_save, -9)
            fatjet_PNet_Xbb_padded = utils.pad_awkward_array(fatjets.particleNetMD_Xbb, n_save, -9)
            fatjet_PNet_XQCD_padded = utils.pad_awkward_array(fatjets.particleNetMD_QCD, n_save, -9)

    for i in range(n_save):
        events["fatjet%s_pt" % str(i+1)] = fatjet_pt_padded[:,i]
        events["fatjet%s_eta" % str(i+1)] = fatjet_eta_padded[:,i]
        events["fatjet%s_phi" % str(i+1)] = fatjet_phi_padded[:,i]
        events["fatjet%s_msoftdrop" % str(i+1)] = fatjet_msoftdrop_padded[:,i]
        events["fatjet%s_mass" % str(i+1)] = fatjet_mass_padded[:,i]
        events["fatjet%s_btag" % str(i+1)] = fatjet_btag_padded[:,i]
        events["fatjet%s_deepbtag_md" % str(i+1)] = fatjet_deepbtag_md_padded[:,i]
        
        if hasattr(fatjets, "particleNetMD_Xqq"):
            events["fatjet%s_particleNet_Tbb" % str(i+1)] = fatjet_PNet_Xbb_padded[:,i] / (  #taken from Hbb meeting 02/24/2021
                                                            1 - fatjet_PNet_Xcc_padded[:,i] 
                                                            - fatjet_PNet_Xqq_padded[:,i] )
            events["fatjet%s_particleNet_Xqq" % str(i+1)] = fatjet_PNet_Xqq_padded[:,i]
            events["fatjet%s_particleNet_Xcc" % str(i+1)] = fatjet_PNet_Xcc_padded[:,i]
            events["fatjet%s_particleNet_Xbb" % str(i+1)] = fatjet_PNet_Xbb_padded[:,i]
            events["fatjet%s_particleNet_XQCD" % str(i+1)] = fatjet_PNet_XQCD_padded[:,i]
                   
    return events

def set_jets(events, jets, options, debug):
    events["n_jets"] = awkward.num(jets)

    n_save = options["jets"]["n_jets_save"]
    jet_pt_padded = utils.pad_awkward_array(jets.pt, n_save, -9)
    jet_eta_padded = utils.pad_awkward_array(jets.eta, n_save, -9)
    jet_id_padded = utils.pad_awkward_array(jets.jetId, n_save, -9)
    jet_btagDeepFlavB_padded = utils.pad_awkward_array(jets.btagDeepFlavB, n_save, -9)

    for i in range(n_save):
        events["jet%s_pt" % str(i+1)] = jet_pt_padded[:,i]
        events["jet%s_eta" % str(i+1)] = jet_eta_padded[:,i]
        events["jet%s_id" % str(i+1)] = jet_id_padded[:,i]
        events["jet%s_bTagDeepFlavB" % str(i+1)] = jet_btagDeepFlavB_padded[:,i]

    return events
