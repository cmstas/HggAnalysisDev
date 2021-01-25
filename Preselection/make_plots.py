import numpy as np
from yahist import Hist1D
from yahist import Hist2D
import awkward as ak
import numba as nb
from looper_utils import deltaR_devfunc1
from looper_utils import deltaR_devfunc

bin_pt1 = np.linspace(0,200,21)
bin_pt2 = np.linspace(0,200,51)
bin_ptom = np.linspace(0,2,20)
bin_eta = np.linspace(-2.5,2.5,20)
bin_phi = np.linspace(-3.2,3.2,20)
bin_bdt = np.linspace(-1,1,21)
bin_iso_lep = np.linspace(0,0.6,10)
bin_deeptau = np.linspace(0,130,131)
bin_met = np.linspace(0,500,101)
bin_njet = np.linspace(0,5,6)
bin_nbjet = np.linspace(0,3,4)
bin_mZ = np.linspace(0,150,30)
bin_dR = np.linspace(0,5,20)

def process_event(weights, evt_vars): #, bjets):
    out_hists = {}
    out_hists["MET"] = Hist1D(ak.to_numpy(evt_vars.MET_pt), bins = bin_met, label="MET", weights = ak.to_numpy(genWeight))
    #out_hists["njets"] = Hist1D(ak.to_numpy(evt_vars.nJet), bins = bin_njet, label="njet", weights = ak.to_numpy(genWeight))
    #out_hists["nbjets"] = Hist1D(ak.num(bjets), bins = bin_bjet) 
    out_hists["weight"] = ak.sum(weights)
    return out_hists

@nb.jit
def getFromIdx(obj, idx):
    l = len(obj)
    o = np.empty(l, dtype=np.float32)
    for i in range(l):
        o[i] = obj[i][idx[i]]
    return o

def process_diphoton(photons, gHidx, mgg, genWeight):
    out_hists = {}
    
    out_hists["pho_pT1"] = Hist1D(ak.to_numpy( getFromIdx(photons.pt, gHidx[:,0])), bins = bin_pt1, weights=  ak.to_numpy(genWeight), label="pho1 pt")
    out_hists["pho_pT2"] = Hist1D(ak.to_numpy( getFromIdx(photons.pt, gHidx[:,1])), bins = bin_pt1, weights=  ak.to_numpy(genWeight), label="pho2 pt")
    out_hists["pho_pTom1"] = Hist1D(ak.to_numpy(getFromIdx(photons.pt, gHidx[:,0])/mgg), bins = bin_ptom, weights=  ak.to_numpy(genWeight), label="pho1 ptom")
    out_hists["pho_pTom2"] = Hist1D(ak.to_numpy(getFromIdx(photons.pt, gHidx[:,1])/mgg), bins = bin_ptom, weights=  ak.to_numpy(genWeight), label="pho2 ptom")
    out_hists["pho_eta1"] = Hist1D(ak.to_numpy(getFromIdx(photons.eta, gHidx[:,0])), bins = bin_eta, weights=  ak.to_numpy(genWeight), label="pho1 eta")
    out_hists["pho_eta2"] = Hist1D(ak.to_numpy(getFromIdx(photons.eta, gHidx[:,1])), bins = bin_eta, weights=  ak.to_numpy(genWeight), label="pho2 eta")
    out_hists["pho_phi1"] = Hist1D(ak.to_numpy(getFromIdx(photons.phi, gHidx[:,0])), bins = bin_phi, weights=  ak.to_numpy(genWeight), label="pho1 phi")
    out_hists["pho_phi2"] = Hist1D(ak.to_numpy(getFromIdx(photons.phi, gHidx[:,1])), bins = bin_phi, weights=  ak.to_numpy(genWeight), label="pho2 phi")
    out_hists["pho_id1"] = Hist1D(ak.to_numpy(getFromIdx(photons.mvaID, gHidx[:,0])), bins = bin_bdt, weights=  ak.to_numpy(genWeight), label="pho1 id")
    out_hists["pho_id2"] = Hist1D(ak.to_numpy(getFromIdx(photons.mvaID, gHidx[:,1])), bins = bin_bdt, weights=  ak.to_numpy(genWeight), label="pho2 id")
    ## need a function to make p4 of diphoton
    return out_hists
    
def process_tau(taus_all, genWeight_all):
    ## add dxy,dz, and explore decay mode
    
    out_hists = {}
    ntau = ak.num(taus_all)
    taus = taus_all[ntau > 0]
    genWeight = genWeight_all[ntau > 0]
    
    if len(taus) == 0:
        return out_hists
    else:
        out_hists["tau_pT1"] = Hist1D(ak.to_numpy(taus.pt[:,0]), bins = bin_pt2, weights=  ak.to_numpy(genWeight), label="tau1 pt")
        out_hists["tau_eta1"] = Hist1D(ak.to_numpy(taus.eta[:,0]), bins = bin_eta, weights=  ak.to_numpy(genWeight), label="tau1 eta")
        out_hists["tau_phi1"] = Hist1D(ak.to_numpy(taus.phi[:,0]), bins = bin_phi, weights=  ak.to_numpy(genWeight), label="tau1 phi")
        out_hists["tau_deeptau_vs_j_1"] = Hist1D(ak.to_numpy(taus.idDeepTau2017v2p1VSjet[:,0]), bins = bin_deeptau, weights=  ak.to_numpy(genWeight), label="tau1 deepTau vs j")
        out_hists["tau_deeptau_vs_m_1"] = Hist1D(ak.to_numpy(taus.idDeepTau2017v2p1VSmu[:,0]), bins = bin_deeptau, weights=  ak.to_numpy(genWeight), label="tau1 deepTau vs mu")
        out_hists["tau_deeptau_vs_e_1"] = Hist1D(ak.to_numpy(taus.idDeepTau2017v2p1VSe[:,0]), bins = bin_deeptau, weights=  ak.to_numpy(genWeight), label="tau1 deepTau vs e")
        out_hists["n_tau"] = Hist1D(ak.num(taus), bins = np.linspace(0,5,6), weights=  ak.to_numpy(genWeight), label = "n taus")
        taus_2 = taus_all[ntau == 2]
        genWeight_2 = genWeight_all[ntau == 2]
        if len(taus_2) == 0:
            return out_hists
        else:
            
            tau0 = taus_2[:,0]
            tau1 = taus_2[:,1]
            mtautau = np.sqrt(2*tau0.pt*tau1.pt*(np.cosh(tau0.eta - tau1.eta) - np.cos(tau0.phi - tau1.phi)))
            #mtautau = (taus_p4c_2[:, 0] + taus_p4c_2[:, 1]).mass
            out_hists["mtautau"] = Hist1D(ak.to_numpy(mtautau), bins = bin_mZ, weights = ak.to_numpy(genWeight_2), label="mtautau")
            
            dR_tautau = deltaR_devfunc1(taus_2)
            out_hists["dR_tautau"] = Hist1D(ak.to_numpy(dR_tautau), bins = bin_dR, weights = ak.to_numpy(genWeight_2), label="dR_tautau") 
            
            out_hists["tau_pT2"] = Hist1D(ak.to_numpy(taus_2.pt[:,1]), bins = bin_pt2, weights=   ak.to_numpy(genWeight_2), label="tau2 pt")
            out_hists["tau_eta2"] = Hist1D(ak.to_numpy(taus_2.eta[:,1]), bins = bin_eta, weights=   ak.to_numpy(genWeight_2), label="tau2 eta")
            out_hists["tau_phi2"] = Hist1D(ak.to_numpy(taus_2.phi[:,1]), bins = bin_phi, weights=   ak.to_numpy(genWeight_2), label="tau2 phi")
            out_hists["tau_deeptau_vs_j_2"] = Hist1D(ak.to_numpy(taus_2.idDeepTau2017v2p1VSjet[:,1]), bins = bin_deeptau, weights=   ak.to_numpy(genWeight_2), label="tau2 deepTau vs j")
            out_hists["tau_deeptau_vs_m_2"] = Hist1D(ak.to_numpy(taus_2.idDeepTau2017v2p1VSmu[:,1]), bins = bin_deeptau, weights=   ak.to_numpy(genWeight_2), label="tau2 deepTau vs mu")
            out_hists["tau_deeptau_vs_e_2"] = Hist1D(ak.to_numpy(taus_2.idDeepTau2017v2p1VSe[:,1]), bins = bin_deeptau, weights=   ak.to_numpy(genWeight_2), label="tau2 deepTau vs e")
            return out_hists


def process_muon(muons_all, genWeight_all):
    out_hists = {}
    nmuon = ak.num(muons_all)
    muons = muons_all[nmuon > 0]
    genWeight = genWeight_all[nmuon > 0]
    if len(muons) == 0:
        return out_hists
    else:
        out_hists["muon_pT1"] = Hist1D(ak.to_numpy(muons.pt[:,0]), bins = bin_pt2, weights=  ak.to_numpy(genWeight), label="mu1 pt")
        out_hists["muon_eta1"] = Hist1D(ak.to_numpy(muons.eta[:,0]), bins = bin_eta, weights=  ak.to_numpy(genWeight), label="mu1 eta")
        out_hists["muon_phi1"] = Hist1D(ak.to_numpy(muons.phi[:,0]), bins = bin_phi, weights=  ak.to_numpy(genWeight), label="mu1 phi")
        out_hists["muon_iso1"] = Hist1D(ak.to_numpy(muons.pfRelIso03_all[:,0]), bins = bin_iso_lep, weights=  ak.to_numpy(genWeight), label="mu1 iso")
        out_hists["n_muon"] = Hist1D(ak.num(muons), bins = np.linspace(0,5,6), weights=  ak.to_numpy(genWeight), label = "n muons")
        
        muons_2 = muons_all[nmuon == 2]
        genWeight_2 = genWeight_all[nmuon == 2]
        if len(muons_2) == 0:
            return out_hists
        else:
            mu0 = muons_2[:,0]
            mu1 = muons_2[:,1]
            mmumu = np.sqrt(2*mu0.pt*mu1.pt*(np.cosh(mu0.eta - mu1.eta) - np.cos(mu0.phi - mu1.phi)))
            #mmumu = (muons_p4c_2[:, 0] + muons_p4c_2[:, 1]).mass
            out_hists["mmumu"] = Hist1D(ak.to_numpy(mmumu), bins = bin_mZ, weights = ak.to_numpy(genWeight_2), label="mmumu")
            
            dR_mumu = deltaR_devfunc1(muons_2)
            out_hists["dR_mumu"] = Hist1D(ak.to_numpy(dR_mumu), bins = bin_dR, weights = ak.to_numpy(genWeight_2), label="dR_mumu") 
            
            out_hists["muon_pT2"] = Hist1D(ak.to_numpy(muons_2.pt[:,1]), bins = bin_pt2, weights=  ak.to_numpy(genWeight_2), label="mu2 pt")
            out_hists["muon_eta2"] = Hist1D(ak.to_numpy(muons_2.eta[:,1]), bins = bin_eta, weights=  ak.to_numpy(genWeight_2), label="mu2 eta")
            out_hists["muon_phi2"] = Hist1D(ak.to_numpy(muons_2.phi[:,1]), bins = bin_phi, weights=  ak.to_numpy(genWeight_2), label="mu2 phi")
            out_hists["muon_iso2"] = Hist1D(ak.to_numpy(muons_2.pfRelIso03_all[:,1]), bins = bin_iso_lep, weights=  ak.to_numpy(genWeight_2), label="mu2 iso")
            return out_hists

def process_electron(electrons_all, genWeight_all):
    out_hists = {}
    
    nelectron = ak.num(electrons_all)
    electrons = electrons_all[nelectron > 0]
    genWeight = genWeight_all[nelectron > 0]
    if len(electrons) == 0:
        return out_hists
    else:
        out_hists["electron_pT1"] = Hist1D(ak.to_numpy(electrons.pt[:,0]), bins = bin_pt2, weights=  ak.to_numpy(genWeight), label="ele1 pt")
        out_hists["electron_eta1"] = Hist1D(ak.to_numpy(electrons.eta[:,0]), bins = bin_eta, weights=  ak.to_numpy(genWeight), label="ele1 eta")
        out_hists["electron_phi1"] = Hist1D(ak.to_numpy(electrons.phi[:,0]), bins = bin_phi, weights=  ak.to_numpy(genWeight), label="ele1 phi")
        out_hists["electron_iso1"] = Hist1D(ak.to_numpy(electrons.pfRelIso03_all[:,0]), bins = bin_iso_lep, weights=  ak.to_numpy(genWeight), label="ele1 iso")
        out_hists["n_electron"] = Hist1D(ak.num(electrons), bins = np.linspace(0,5,6),   weights = ak.to_numpy(genWeight), label = "n electrons")
        
        electrons_2 = electrons_all[nelectron == 2]
        genWeight_2 = genWeight_all[nelectron == 2]
        if len(electrons_2) == 0:
            return out_hists
        else:
            ele0 = electrons_2[:,0]
            ele1 = electrons_2[:,1]
            mee = np.sqrt(2*ele0.pt*ele1.pt*(np.cosh(ele0.eta - ele1.eta) - np.cos(ele0.phi - ele1.phi)))
            #mee = (electrons_p4c_2[:, 0] + electrons_p4c_2[:, 1]).mass
            out_hists["mee"] = Hist1D(ak.to_numpy(mee), bins = bin_mZ, weights = ak.to_numpy(genWeight_2), label="mee")
            
            dR_ee = deltaR_devfunc1(electrons_2)
            out_hists["dR_ee"] = Hist1D(ak.to_numpy(dR_ee), bins = bin_dR, weights = ak.to_numpy(genWeight_2), label="dR_ee") 
            
            out_hists["electron_pT2"] = Hist1D(ak.to_numpy(electrons_2.pt[:,1]), bins = bin_pt2, weights=  ak.to_numpy(genWeight_2), label="ele2 pt")
            out_hists["electron_eta2"] = Hist1D(ak.to_numpy(electrons_2.eta[:,1]), bins = bin_eta, weights=  ak.to_numpy(genWeight_2), label="eta2 eta")
            out_hists["electron_phi2"] = Hist1D(ak.to_numpy(electrons_2.phi[:,1]), bins = bin_phi, weights=  ak.to_numpy(genWeight_2), label="eta2 phi")
            out_hists["electron_iso2"] = Hist1D(ak.to_numpy(electrons_2.pfRelIso03_all[:,1]), bins = bin_iso_lep, weights=  ak.to_numpy(genWeight_2), label="eta2 iso")
            return out_hists


def process_1tau_1lep(taus_all, muons_all, electrons_all, genWeight_all):

    out_hists = {}
    
    ntau = ak.num(taus_all)
    nmuon = ak.num(muons_all)
    nelectron = ak.num(electrons_all)
    
    mask_tau_e = (ntau == 1) & (nelectron == 1) & (nmuon == 0)
    mask_tau_mu = (ntau == 1) & (nmuon == 1) & (nelectron == 0)
    
    taus_taue = taus_all[mask_tau_e]
    electrons_taue = electrons_all[mask_tau_e]
    genWeight_taue = genWeight_all[mask_tau_e]
    
    taus_taumu = taus_all[mask_tau_mu]
    muons_taumu = muons_all[mask_tau_mu]
    genWeight_taumu = genWeight_all[mask_tau_mu]
    
    if len(taus_taue) > 0:
        
        tau0 = taus_taue[:,0]
        ele0 = electrons_taue[:,0]
        mtaue = np.sqrt(2*tau0.pt*ele0.pt*(np.cosh(tau0.eta - ele0.eta) - np.cos(tau0.phi - ele0.phi)))
        #mtaue = (taus_taue[:,0] + electrons_taue[:,0]).mass
        out_hists["mtaue"] = Hist1D(ak.to_numpy(mtaue), bins = bin_mZ, weights = ak.to_numpy(genWeight_taue), label="mtaue") 
        
        dR_tau_e = deltaR_devfunc(taus_taue, electrons_taue)
        out_hists["dR_tau_e"] = Hist1D(ak.to_numpy(dR_tau_e), bins = bin_dR, weights = ak.to_numpy(genWeight_taue), label="dR_taue") 
    if len(taus_taumu) > 0:
        
        tau0 = taus_taumu[:,0]
        mu0 = muons_taumu[:,0]
        mtaumu = np.sqrt(2*tau0.pt*mu0.pt*(np.cosh(tau0.eta - mu0.eta) - np.cos(tau0.phi - mu0.phi)))
        #mtaumu = (taus_taumu[:,0] + muons_taumu[:,0]).mass
        out_hists["mtaumu"] = Hist1D(ak.to_numpy(mtaumu), bins = bin_mZ, weights = ak.to_numpy(genWeight_taumu), label="mtaumu") 
        
        dR_tau_mu = deltaR_devfunc(taus_taumu, muons_taumu)
        out_hists["dR_tau_mu"] = Hist1D(ak.to_numpy(dR_tau_mu), bins = bin_dR, weights = ak.to_numpy(genWeight_taumu), label="dR_taumu") 
    return out_hists
