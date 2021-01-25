import numba as nb
import math
import numpy as np
import awkward as ak

@nb.jit
def deltaphi_devfunc(phi1, phi2):
    dphi = phi1 - phi2
    out_dphi = float(0)
    
    if dphi > math.pi:
        dphi = dphi - 2 * math.pi
        out_dphi = dphi
    elif (dphi + math.pi) < 0:
        dphi = dphi + 2 * math.pi
        out_dphi = dphi
    else:
        out_dphi = dphi
    return out_dphi

@nb.jit
def deltaR_devfunc(objs1, objs2):
    if len(objs1) != len(objs2):
        return np.array([-1], dtype=np.float32)
    
    npair = len(objs1)
    dRs = np.zeros(npair, dtype=np.float32)
    for i in range(npair):
        ## in this extreme example, there is only 1 tau or 1 e or 1 mu in the event
        eta1 = objs1[i][0].eta
        phi1 = objs1[i][0].phi
        eta2 = objs2[i][0].eta
        phi2 = objs2[i][0].phi
        dR = np.sqrt((eta1-eta2)**2 + deltaphi_devfunc(phi1,phi2)**2)
        dRs[i] = dR
    return dRs

@nb.jit
def deltaR_devfunc1(objs1):
    
    npair = len(objs1)
    dRs = np.zeros(npair, dtype=np.float32)
    for i in range(npair):
        ## in this extreme example, there is only 1 tau or 1 e or 1 mu in the event
        eta1 = objs1[i][0].eta
        phi1 = objs1[i][0].phi
        eta2 = objs1[i][1].eta
        phi2 = objs1[i][1].phi
        dR = np.sqrt((eta1-eta2)**2 + deltaphi_devfunc(phi1,phi2)**2)
        dRs[i] = dR
    return dRs

@nb.jit
def mask_by_mll_dR2(lep1, lep2, nlep1, nlep2, mll_lim, dR_lim, phos, gHidxs, dR_lim2):
    nEvents = len(lep1)
    mask = np.zeros(nEvents, dtype=int64) > 0
    for i in range(nEvents):
        if not (nlep1[i] and nlep2[i]): continue
        l1 = lep1[i][0]
        l2 = lep2[i][0]
        pho1 = phos[i][gHidxs[i][0]]
        pho2 = phos[i][gHidxs[i][1]]
        dR_pho1_l1 = np.sqrt((pho1.eta-l1.eta)**2 + deltaphi_devfunc(pho1.phi, l1.phi)**2)  
        dR_pho2_l1 = np.sqrt((pho2.eta-l1.eta)**2 + deltaphi_devfunc(pho2.phi, l1.phi)**2)  
        dR_pho1_l2 = np.sqrt((pho1.eta-l2.eta)**2 + deltaphi_devfunc(pho1.phi, l2.phi)**2)  
        dR_pho2_l2 = np.sqrt((pho2.eta-l2.eta)**2 + deltaphi_devfunc(pho2.phi, l2.phi)**2)  
        
        if (dR_pho1_l1 < dR_lim2) or (dR_pho2_l1 < dR_lim2) or ((dR_pho1_l2 < dR_lim2)) or (dR_pho2_l2 < dR_lim2):
            # either lepton is too close to photon
            continue
        
        mll = np.sqrt(2*l1.pt*l2.pt*(np.cosh(l1.eta - l2.eta) - np.cos(l1.phi - l2.phi)))
        dR = np.sqrt((l1.eta-l2.eta)**2 + deltaphi_devfunc(l1.phi, l2.phi)**2)
        if (mll <= mll_lim) or (dR < dR_lim): continue
        mask[i] = True 
    return mask 

@nb.jit
def mask_by_mll_dR(lep1, nlep1, mll_lim, dR_lim, phos, gHidxs, dR_lim2):
    nEvents = len(lep1)
    mask = np.zeros(nEvents, dtype=int64) > 0
    for i in range(nEvents):
        if not nlep1[i]: continue
        l1 = lep1[i][0]
        l2 = lep1[i][1]
        pho1 = phos[i][gHidxs[i][0]]
        pho2 = phos[i][gHidxs[i][1]]
        dR_pho1_l1 = np.sqrt((pho1.eta-l1.eta)**2 + deltaphi_devfunc(pho1.phi, l1.phi)**2)  
        dR_pho2_l1 = np.sqrt((pho2.eta-l1.eta)**2 + deltaphi_devfunc(pho2.phi, l1.phi)**2)  
        dR_pho1_l2 = np.sqrt((pho1.eta-l2.eta)**2 + deltaphi_devfunc(pho1.phi, l2.phi)**2)  
        dR_pho2_l2 = np.sqrt((pho2.eta-l2.eta)**2 + deltaphi_devfunc(pho2.phi, l2.phi)**2)  
        
        if (dR_pho1_l1 < dR_lim2) or (dR_pho2_l1 < dR_lim2) or ((dR_pho1_l2 < dR_lim2)) or (dR_pho2_l2 < dR_lim2):
            # either lepton is too close to photon
            continue
        mll = np.sqrt(2*l1.pt*l2.pt*(np.cosh(l1.eta - l2.eta) - np.cos(l1.phi - l2.phi)))
        dR = np.sqrt((l1.eta-l2.eta)**2 + deltaphi_devfunc(l1.phi, l2.phi)**2)
        if (mll <= mll_lim) or (dR < dR_lim): continue
        mask[i] = True 
    return mask 

@nb.jit
def mask_by_dR_l_pho(lep, phos, gHidxs, evt_mask, dR_lim):
    nEvents = len(lep)
    mask = np.zeros(nEvents, dtype=np.int64) > 0
    for i in range(nEvents):
        if not evt_mask[i]: continue
        l = lep[i]
        pho1 = phos[i][gHidxs[i][0]]
        pho2 = phos[i][gHidxs[i][1]]
        dR_pho1_l = np.sqrt((pho1.eta-l.eta)**2 + deltaphi_devfunc(pho1.phi, l.phi)**2)  
        dR_pho2_l = np.sqrt((pho2.eta-l.eta)**2 + deltaphi_devfunc(pho2.phi, l.phi)**2)  
        
        if (dR_pho1_l < dR_lim) or (dR_pho2_l < dR_lim):
            # either lepton is too close to photon
            continue
        mask[i] = True 
    return mask 

def mask_by_dR(objs1, objs2, dR_lim):
    offsets, contents = mask_by_dR_nb(objs1, objs2, dR_lim)
    mask_by_dR_listoffsetarray = ak.layout.ListOffsetArray64(ak.layout.Index64(offsets), ak.layout.NumpyArray(contents) )
    return ak.Array(mask_by_dR_listoffsetarray)    
    '''
    return a mask that is the same size as obj1
    if obj1 is close to any obj2 in the same event, False, else True
    '''

@nb.jit
def mask_by_dR_nb(objs1, objs2, dR_lim):
    nEvents = len(objs1)
    nobj1s = np.int64(0)
    for i in range(nEvents):
        nobj1s += len(objs1[i])

    mask_offsets = np.empty(nEvents+1, np.int64)
    mask_offsets[0] = 0
    mask_contents = np.empty(nobj1s, np.bool_)
    for i in range(nEvents):
        mask_offsets[i+1] = mask_offsets[i]
        objs1_evt = objs1[i]
        objs2_evt = objs2[i]
        for j in range(len(objs1_evt)):
            obj1 = objs1_evt[j] 
            mask_contents[mask_offsets[i+1]] = True 
            for k in range(len(objs2_evt)):
                obj2 = objs2_evt[k]
                dR = np.sqrt((obj1.eta-obj2.eta)**2 + deltaphi_devfunc(obj1.phi, obj2.phi)**2)  
                if (dR < dR_lim):
                    mask_contents[mask_offsets[i+1]] = False
                    break
            mask_offsets[i+1] += 1

    return mask_offsets, mask_contents 

@nb.jit
def mask_by_dR_perEvent(obj1, obj2, evt_mask, dR_lim):
    nEvents = len(obj1)
    mask = np.zeros(nEvents, dtype=np.int64) > 0
    for i in range(nEvents):
        if not evt_mask[i]: continue
        p1 = obj1[i]
        p2 = obj2[i]
        dR = np.sqrt((p1.eta-p2.eta)**2 + deltaphi_devfunc(p1.phi, p2.phi)**2)  
        
        if (dR < dR_lim):
            # either lepton is too close to photon
            continue
        mask[i] = True 
    return mask 

@nb.jit
def mask_by_mass(obj1, obj2, evt_mask, mass_lim):
    nEvents = len(obj1)
    mask = np.zeros(nEvents, dtype=np.int64) > 0
    for i in range(nEvents):
        if not evt_mask[i]: continue
        p1 = obj1[i]
        p2 = obj2[i]
        m = np.sqrt(2*p1.pt*p2.pt*(np.cosh(p1.eta - p2.eta) - np.cos(p1.phi - p2.phi)))
        
        if (m < mass_lim):
            # either lepton is too close to photon
            continue
        mask[i] = True 
    return mask 

@nb.jit
def mask_by_dR_mll_0lep_2tau(taus, dR_lims, mll_lims):
    nEvents = len(taus)
    mask = np.zeros(nEvents, dtype=np.int64) > 0
    for i in range(nEvents):
        # if there is no tau in this event (masked by ntau = 2 requirement early on)
        if len(taus[i]) != 2: continue
        tau1 = taus[i][0]
        tau2 = taus[i][1]
        m = np.sqrt(2*tau1.pt*tau2.pt*(np.cosh(tau1.eta - tau2.eta) - np.cos(tau1.phi - tau2.phi)))
        dR = np.sqrt((tau1.eta-tau2.eta)**2 + deltaphi_devfunc(tau1.phi, tau2.phi)**2)  

        if (m < mll_lims[0] or m > mll_lims[1]): continue
        if (dR < dR_lims[0] or dR > dR_lims[1]): continue

        mask[i] = True

    return mask

@nb.jit
def mask_by_dR_mll_1lep_1tau(taus, leps, dR_lims, mll_lims):
    nEvents = len(taus)
    mask = np.zeros(nEvents, dtype=np.int64) > 0
    for i in range(nEvents):
        # if there is no tau in this event (masked by ntau = 2 requirement early on)
        if len(taus[i]) != 1: continue
        if len(leps[i]) != 1: continue
        tau1 = taus[i][0]
        lep1 = leps[i][0]
        m = np.sqrt(2*tau1.pt*lep1.pt*(np.cosh(tau1.eta - lep1.eta) - np.cos(tau1.phi - lep1.phi)))
        dR = np.sqrt((tau1.eta-lep1.eta)**2 + deltaphi_devfunc(tau1.phi, lep1.phi)**2)  

        if (m < mll_lims[0] or m > mll_lims[1]): continue
        if (dR < dR_lims[0] or dR > dR_lims[1]): continue

        mask[i] = True

    return mask
