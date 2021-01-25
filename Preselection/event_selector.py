from yahist import Hist1D
#import uproot_methods
import awkward as ak
import uproot
import numba as nb
import numpy as np


def get_gHidx(args):
    '''
    This needs to be inserted in prepare_inputs
    Consider make flat indexing, otherwise don't work
    '''
    fname,entrystart,entrystop = args
    f = uproot.open(fname)
    t = f["Events"]
    idx_keys = t.keys(filter_name="gHidx")
    gHidx = t.arrays( idx_keys, entry_start=entrystart, entry_stop=entrystop, library="ak", how="zip" )
    return gHidx

def prepare_inputs(args, obj_list, isData=False):
    fname,entrystart,entrystop = args
    f = uproot.open(fname)
    t = f["Events"]
    
    #keys_to_save = t.keys(filter_name="Category_*") + ["gHidx", "ggMass"]
    #keys_to_save = ["gHidx", "ggMass"]
    keys_to_save = ["event"]

    if isData == False:
        keys_to_save += ["genWeight"]

    if "electron" in obj_list:
        electron_keys = t.keys(filter_name="Electron_*") 
        keys_to_save +=  electron_keys
    if "muon" in obj_list:    
        muon_keys = t.keys(filter_name="Muon_*") 
        keys_to_save +=  muon_keys
    if "tau" in obj_list:
        tau_keys = t.keys(filter_name="Tau_*") 
        keys_to_save +=  tau_keys
    if "photon" in obj_list:
        photon_keys = t.keys(filter_name="Photon_*") 
        keys_to_save +=  photon_keys
    if "category" in obj_list:
        category_keys  = t.keys(filter_name="Category_*")
        keys_to_save += category_keys
    #if "idx" in obj_list:
    #    idx_keys = t.keys(filter_name="gHidx")
    #    keys_to_save += idx_keys
    if "others" in obj_list:
        evt_vars_keys = t.keys(filter_name=["nJet", "MET_pt", "ggMass"]) 
        keys_to_save +=  evt_vars_keys

    events = t.arrays( keys_to_save , entry_start=entrystart, entry_stop=entrystop, library="ak", how="zip" )
    if isData:
        events.genWeight = np.array(np.ones(len(events)), np.int64)
    return events
    
@nb.jit
def select_photon_byEvent(photon, gHIdx, mgg):
    nEvents = len(photon)
    mask_init = np.zeros(nEvents, dtype=np.int64)
    mask_dipho =  mask_init > 0 # all False
    for i in range(nEvents):
        phoidx1 = gHIdx[i][0]
        phoidx2 = gHIdx[i][1]
        pho1 = photon[i][phoidx1]
        pho2 = photon[i][phoidx2]
        if (pho1.mvaID < -0.7) | (pho2.mvaID < -0.7): continue
        if (pho1.pt/mgg[i] < 0.3) | (pho2.pt/mgg[i] < 0.25): continue
        if mgg[i] < 100: continue
        mask_dipho[i] = True 
    return mask_dipho

@nb.jit
def select_photon_nb(photon, gHIdx, mgg):
    nEvents = len(photon)
    nPhotons = np.int64(0)
    for i in range(nEvents):
        nPhotons += len(photon[i])

    mask_offsets = np.empty(nEvents+1, np.int64)
    mask_offsets[0] = 0
    mask_contents = np.empty(nPhotons, np.bool_)
    for i in range(nEvents):
        mask_offsets[i+1] = mask_offsets[i]
        phos = photon[i]
        leadidx = gHIdx[i][0]
        subleadidx = gHIdx[i][1]
        for j in range(len(phos)):
            pho = phos[j] 
            if (pho.mvaID < -0.7) or ((j != leadidx ) and (j != subleadidx)):
                mask_contents[mask_offsets[i+1]] = False
            elif ((j == leadidx) and (pho.pt/mgg[i] < 0.3)):
                mask_contents[mask_offsets[i+1]] = False
            elif ((j == subleadidx) and (pho.pt/mgg[i] < 0.3)):
                mask_contents[mask_offsets[i+1]] = False
            else:
                mask_contents[mask_offsets[i+1]] = True 

            mask_offsets[i+1] += 1

    return mask_offsets, mask_contents 

def select_photon(photon, gHIdx, mgg):
    offsets, contents = select_photon_nb(photon, gHIdx, mgg)
    mask_photons_listoffsetarray = ak.layout.ListOffsetArray64(ak.layout.Index64(offsets), ak.layout.NumpyArray(contents) )
    return ak.Array(mask_photons_listoffsetarray)    

def select_electron(electron, isTight):
        
    if isTight == True:
        cut_ele_pt = electron.pt > 25
        cut_ele_eta = abs(electron.eta) < 2.5
        cut_ele_dxy = abs(electron.dxy) < 0.045
        cut_ele_dz = abs(electron.dz) < 0.2
        cut_ele_id = electron.mvaFall17V2Iso_WP80 == True
        
        # build mask
        mask_ele = cut_ele_pt & cut_ele_eta & cut_ele_dxy & cut_ele_dz & cut_ele_id
        return mask_ele    
    else:
        cut_ele_pt = electron.pt > 10 
        cut_ele_eta = abs(electron.eta) < 2.5
        cut_ele_dxy = abs(electron.dxy) < 0.045
        cut_ele_dz = abs(electron.dz) < 0.2
        cut_ele_id = ((electron.mvaFall17V2Iso_WP90 == True) | ((electron.mvaFall17V2noIso_WP90 == True) & (electron.pfRelIso03_all < 0.3)))
        
        # build mask
        mask_ele = cut_ele_pt & cut_ele_eta & cut_ele_dxy & cut_ele_dz & cut_ele_id
        return mask_ele    

def select_muon(muon, isTight):

    if isTight == True:
        cut_mu_pt = muon.pt > 20
        cut_mu_eta = abs(muon.eta) < 2.4
        cut_mu_dxy = abs(muon.dxy) < 0.045
        cut_mu_dz = abs(muon.dz) < 0.2
        cut_mu_id = muon.tightId >= 1
        cut_mu_iso = muon.pfRelIso04_all < 0.15

        # build mask
        mask_mu = cut_mu_pt & cut_mu_eta & cut_mu_dxy & cut_mu_dz & cut_mu_id & cut_mu_iso
        return mask_mu
    else:
        cut_mu_pt = muon.pt > 10
        cut_mu_eta = abs(muon.eta) < 2.4
        cut_mu_dxy = abs(muon.dxy) < 0.045
        cut_mu_dz = abs(muon.dz) < 0.2
        cut_mu_iso = muon.pfRelIso03_all < 0.3

        # build mask
        mask_mu = cut_mu_pt & cut_mu_eta & cut_mu_dxy & cut_mu_dz & cut_mu_iso
        return mask_mu

def select_tau(tau, cat, isTight):
    # cat = tau_mu, tau_e, tau_tau
    deepTauID = {"tau_mu": (4,8,8), "tau_e": (32,8,8), "tau_tau": (2,8,1), "all": (2,8,1)} 

    cut_tau_pt = tau.pt > 20
    cut_tau_eta = abs(tau.eta) < 2.3
    cut_tau_decayMode = tau.idDecayModeNewDMs == True
    cut_tau_deepTau_vs_e = tau.idDeepTau2017v2p1VSe >= deepTauID[cat][0] 
    cut_tau_deepTau_vs_j = tau.idDeepTau2017v2p1VSjet >= deepTauID[cat][1] 
    cut_tau_deepTau_vs_m = tau.idDeepTau2017v2p1VSmu >= deepTauID[cat][2] 
    cut_tau_dz = abs(tau.dz) < 0.2
    mask_tau = cut_tau_pt & cut_tau_eta & cut_tau_decayMode & \
               cut_tau_deepTau_vs_e & cut_tau_deepTau_vs_j & cut_tau_deepTau_vs_m & \
               cut_tau_dz 
    if isTight == True:
        #print ("do tight tau")
        cut_tau_deepTau_vs_j_tight = tau.idDeepTau2017v2p1VSjet >= 16
        return mask_tau & cut_tau_deepTau_vs_j_tight
    else:
        #print ("do loose tau")
        return mask_tau

