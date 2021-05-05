import numpy
import awkward
import vector
import numba


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
    cosTheta = compute_helicity_angles(leadingTauVector, SVFitVector, HggVector)
    events["cos_theta_helicity"] = awkward.from_numpy(cosTheta)

    return events


@numba.njit
def compute_helicity_angles(daughterVector, parentVector):
    nEvents = len(daughterVector)
    cosTheta = numpy.zeros(nEvents)
    for i in range(nEvents):
        parent = parentVector[i]
        if parent.pt < 0:
            cosTheta[i] = -9
            continue
        daughter = daughterVector[i]
        daughterInParentFrame = daughter.boost_p4(-parent)
        cosTheta[i] = parent.dot(daughterInParentFrame)/(parent.mag * daughter.mag)
        cosTheta[i] = (parent.x * daughterInParentFrame.x + parent.y * daughterInParentFrame.y + parent.z * daughterInParentFrame.z)/(parent.mag * daughterInParentFrame.mag)
    return cosTheta
