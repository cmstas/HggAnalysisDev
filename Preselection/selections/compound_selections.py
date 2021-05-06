import numpy
import awkward
import vector
import numba
import selections.selection_utils as utils

def compound_selections(events, options, debug):

    # dphi(MET, tau1)
    tauVector = vector.awk({"pt": events['tau1_pt'], "eta": events['tau1_eta'], "phi": events['tau1_phi']})
    METVector = vector.awk({"pt": events["MET_pt"], "phi": events["MET_phi"]})

    events["dphi_MET_tau1"] = tauVector.deltaphi(METVector)

    return events


def set_helicity_angles(events, taus, photons):

    leadingTauVector = vector.awk({"pt": events['tau1_pt'], "eta": events['tau1_eta'], "phi": events['tau1_phi'], "mass":events['tau1_mass']})

    SVFitVector = vector.awk({"pt": events["pt_tautauSVFitLoose"], "eta": events["eta_tautauSVFitLoose"], "phi": events["phi_tautauSVFitLoose"], "mass": events["m_tautauSVFitLoose"]})
    g1Vector = vector.awk({"pt": photons[:,0].pt, "eta": photons[:,0].eta, "phi": photons[:,0].phi, "mass": photons[:,0].mass})
    g2Vector = vector.awk({"pt": photons[:,1].pt, "eta": photons[:,1].eta, "phi": photons[:,1].phi, "mass": photons[:,1].mass})
    HggVector = g1Vector + g2Vector
    cosTheta = compute_helicity_angles(leadingTauVector, SVFitVector)
    events["cos_theta_helicity"] = awkward.from_numpy(cosTheta)

    return events


def set_gen_helicity_angles(events, genBranches, options, debug):
    if genBranches is None:
        events["cos_theta_helicity_gen"] = awkward.from_numpy(-9 * numpy.ones(len(events)))
    else:
        tau_idxs = (abs(genBranches.pdgId) == 15) & ((genBranches.status == 2) | (genBranches.status == 23))

        tau_idxs = tau_idxs[ak.sum(tau_idxs, axis = 1) == 2] # Require two prompt taus
        motherOfTaus = genBranches.genPartIdxMother[tau_idxs]

        VToTauMask = motherOfTaus[(genBranches.pdgId[motherOfTaus] == 23) | (genBranches.pdgId[motherOfTaus] == 25)] # Selecting only those Z/H whose daughters are taus
        genVPt = pad_awkward_array(genBranches.pt[VToTauMask], 2, -1)
        genVEta = pad_awkward_array(genBranches.eta[VToTauMask], 2, -1)
        genVPhi = pad_awkward_array(genBranches.phi[VToTauMask], 2, -1)
        genVMass = pad_awkward_array(genBranches.mass[VToTauMask], 2, -1)

        leadingTauPt = pad_awkward_array(genBranches.pt[tau_idxs], 2, -1)[:,0]
        leadingTauEta = pad_awkward_array(genBranches.eta[tau_idxs], 2, -1)[:,0]
        leadingTauPhi = pad_awkward_array(genBranches.phi[tau_idxs], 2, -1)[:,0]
        leadingTauMass = pad_awkward_array(genBranches.mass[tau_idxs], 2, -1)[:,0]

        genVVector = vector.awk({"pt":genVPt, "eta":genVEta, "phi":genVPhi, "mass":genVMass})
        leadingTauVector = vector.awk({"pt":leadingTauPt, "eta":leadingTauEta, "phi":leadingTauPhi, "mass":leadingTauMass})

        cosThetaGen = compute_helicity_angles(leadingTauVector, genVVector)
        events["cos_theta_helicity_gen"] = awkward.from_numpy(cosThetaGen)

    return events

@numba.njit
def compute_helicity_angles(daughterVector, parentVector):
    nEvents = len(daughterVector)
    cosTheta = numpy.ones(nEvents) * -9
    for i in range(nEvents):
        parent = parentVector[i]
        if parent.pt < 0:
            continue
        daughter = daughterVector[i]
        daughterInParentFrame = daughter.boost_p4(-parent)
        vParent = parent.to_Vector3D()
        vDaughter = daughterInParentFrame.to_Vector3D()
        cosTheta[i] = vParent.dot(vDaughter)/(vParent.mag * vDaughter.mag)
    return cosTheta
