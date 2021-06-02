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
    g1Vector = vector.awk({"pt": photons.pt[:,0], "eta": photons.eta[:,0], "phi": photons.phi[:,0], "mass": photons.mass[:,0]})
    g2Vector = vector.awk({"pt": photons.pt[:,1], "eta": photons.eta[:,1], "phi": photons.phi[:,1], "mass": photons.mass[:,1]})
    cosTheta = compute_helicity_angles(leadingTauVector, SVFitVector)
    events["cos_theta_helicity"] = awkward.from_numpy(cosTheta)
    HggVector = g1Vector + g2Vector
    cosThetaPhoton = compute_helicity_angles(g1Vector, HggVector)
    events["cos_theta_photon_helicity"] = awkward.from_numpy(cosThetaPhoton)

    return events



def set_gen_helicity_angles(events, genBranches, options, debug):
    if genBranches is None:
        events["cos_theta_helicity_gen"] = awkward.from_numpy(-9 * numpy.ones(len(events)))
    else:
        tau_idxs = (abs(genBranches.pdgId) == 15) #& ((genBranches.status == 2) | (genBranches.status == 23))

        motherOfTaus = genBranches.genPartIdxMother[tau_idxs]
        VToTauMask = motherOfTaus[(genBranches.pdgId[motherOfTaus] == 23) | (genBranches.pdgId[motherOfTaus] == 25)] # Selecting only those Z/H whose daughters are taus
        genVPt = utils.pad_awkward_array(genBranches.pt[VToTauMask], 2, -1)[:,0]
        genVEta = utils.pad_awkward_array(genBranches.eta[VToTauMask], 2, -1)[:,0]
        genVPhi = utils.pad_awkward_array(genBranches.phi[VToTauMask], 2, -1)[:,0]
        genVMass = utils.pad_awkward_array(genBranches.mass[VToTauMask], 2, -1)[:,0]

        decayTauIndices = awkward.from_numpy(mapMotherToDaughter(VToTauMask, genBranches.genPartIdxMother).astype(int)) # Indices of all the decay taus

        # Awkward array redneck engineering right here - This shit works, please don't ask me why
        fancyIndexedTauIndices = awkward.unflatten(awkward.mask(decayTauIndices, decayTauIndices > 0), counts = 1, axis = 0)
        leadingTauPt = awkward.fill_none(genBranches.pt[fancyIndexedTauIndices], -9)[:,0]
        leadingTauEta = awkward.fill_none(genBranches.eta[fancyIndexedTauIndices], -9)[:,0]
        leadingTauPhi = awkward.fill_none(genBranches.phi[fancyIndexedTauIndices], -9)[:,0]
        leadingTauMass = awkward.fill_none(genBranches.mass[fancyIndexedTauIndices], -9)[:,0]

#        leadingTauPt = utils.pad_awkward_array(genBranches.pt[tau_idxs], 2, -1)[:,0]
#        leadingTauEta = utils.pad_awkward_array(genBranches.eta[tau_idxs], 2, -1)[:,0]
#        leadingTauPhi = utils.pad_awkward_array(genBranches.phi[tau_idxs], 2, -1)[:,0]
#        leadingTauMass = utils.pad_awkward_array(genBranches.mass[tau_idxs], 2, -1)[:,0]

        genVVector = vector.awk({"pt":genVPt, "eta":genVEta, "phi":genVPhi, "mass":genVMass})
        leadingTauVector = vector.awk({"pt":leadingTauPt, "eta":leadingTauEta, "phi":leadingTauPhi, "mass":leadingTauMass})

        cosThetaGen = compute_helicity_angles(leadingTauVector, genVVector)
        events["cos_theta_helicity_gen"] = awkward.from_numpy(cosThetaGen)
        events["tau1_pt_gen"] = leadingTauPt
        events["tau1_eta_gen"] = leadingTauEta
        events["parentBoson_pt_gen"] = genVPt
        events["parentBoson_eta_gen"] = genVEta

        photon_idxs = (abs(genBranches.pdgId) == 22)
        motherOfPhotons = genBranches.genPartIdxMother[photon_idxs]
        HToggMask = motherOfPhotons[(genBranches.pdgId[motherOfPhotons] == 25)]
        genHPt = utils.pad_awkward_array(genBranches.pt[HToggMask], 2, -1)[:,0]
        genHEta = utils.pad_awkward_array(genBranches.eta[HToggMask], 2, -1)[:,0]
        genHPhi = utils.pad_awkward_array(genBranches.phi[HToggMask], 2, -1)[:,0]
        genHMass = utils.pad_awkward_array(genBranches.mass[HToggMask], 2, -1)[:,0]

        leadingGammaPt = utils.pad_awkward_array(genBranches.pt[photon_idxs], 2, -1)[:,0]
        leadingGammaEta = utils.pad_awkward_array(genBranches.eta[photon_idxs], 2, -1)[:,0]
        leadingGammaPhi = utils.pad_awkward_array(genBranches.phi[photon_idxs], 2, -1)[:,0]
        leadingGammaMass = utils.pad_awkward_array(genBranches.mass[photon_idxs], 2, -1)[:,0]

        genHVector = vector.awk({"pt":genHPt, "eta":genHEta, "phi":genHPhi, "mass":genHMass})
        leadingPhotonVector = vector.awk({"pt":leadingGammaPt, "eta":leadingGammaEta, "phi":leadingGammaPhi, "mass":leadingGammaMass})

        cosThetaPhotonGen = compute_helicity_angles(leadingPhotonVector, genHVector)
        events["cos_theta_photon_helicity_gen"] = awkward.from_numpy(cosThetaPhotonGen)
        events["gamma1_pt_gen"] = leadingGammaPt
        events["gamma1_eta_gen"] = leadingGammaEta
        events["Hgg_pt_gen"] = genHPt
        events["Hgg_eta_gen"] = genHEta

    return events


def set_category(events):
    # manually set category and then compare it with Category_pairsLoose
    a = numpy.ones(len(events)) * -1
    a[(events.muon1_charge * events.muon2_charge ) < 0] = 4
    a[(a < 0) & (events.muon1_charge * events.ele1_charge < 0)] = 6
    a[(a < 0) & (events.muon1_charge * events.ele2_charge < 0)] = 6
    a[(a < 0) & (events.ele1_charge * events.ele2_charge < 0)] = 5
    a[(a < 0) & (events.muon1_charge * events.tau1_charge < 0) & (events.n_muons == 1) & (events.n_electrons == 0)] = 1
    a[(a < 0) & (events.muon1_charge * events.tau2_charge < 0) & (events.n_muons == 1) & (events.n_electrons == 0)] = 1
    a[(a < 0) & (events.ele1_charge * events.tau1_charge < 0) & (events.n_electrons == 1) & (events.n_muons == 0)] = 2
    a[(a < 0) & (events.ele1_charge * events.tau2_charge < 0) & (events.n_electrons == 1) & (events.n_muons == 0)] = 2
    a[(a < 0) & (events.tau1_charge * events.tau2_charge < 0) & (events.n_muons == 0) & (events.n_electrons == 0)] = 3

    return a


def set_visible_columns(events):
    decay_1_pt = numpy.zeros(len(events))
    decay_1_eta = numpy.zeros(len(events))
    decay_1_phi = numpy.zeros(len(events))
    decay_1_mass = numpy.zeros(len(events))
    decay_1_pdgId = numpy.zeros(len(events))

    decay_2_pt = numpy.zeros(len(events))
    decay_2_eta = numpy.zeros(len(events))
    decay_2_phi = numpy.zeros(len(events))
    decay_2_mass = numpy.zeros(len(events))
    decay_2_pdgId = numpy.zeros(len(events))

    # if conditions - giant wall of text!
    selection = events.Category_pairsLoose == 3
    decay_1_pt[selection] = events[selection].tau1_pt
    decay_1_eta[selection] = events[selection].tau1_eta
    decay_1_phi[selection] = events[selection].tau1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (1.77686)
    decay_1_pdgId[selection] = 15 * events.tau1_charge[selection]

    decay_2_pt[selection] = events[selection].tau2_pt
    decay_2_eta[selection] = events[selection].tau2_eta
    decay_2_phi[selection] = events[selection].tau2_phi
    decay_2_mass[selection] = numpy.ones(events[selection]) * (1.77686)
    decay_2_pdgId[selection] = 15 * events.tau2_charge[selection]

    selection = (events.Category_pairsLoose == 1) & (events.muon1_charge * events.tau1_charge < 0)

    decay_1_pt[selection] = events[selection].muon1_pt
    decay_1_eta[selection] = events[selection].muon1_eta
    decay_1_phi[selection] = events[selection].muon1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.105658)
    decay_1_pdgId[selection] = 13 * events.muon1_charge[selection]

    decay_2_pt[selection] = events[selection].tau1_pt
    decay_2_eta[selection] = events[selection].tau1_eta
    decay_2_phi[selection] = events[selection].tau1_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (1.77686)
    decay_2_pdgId[selection] = 15 * events.tau1_charge[selection]

    selection = (events.Category_pairsLoose == 1) & (events.muon1_charge * events.tau2_charge < 0) & (events.muon1_charge * events.tau1_charge >= 0)

    decay_1_pt[selection] = events[selection].muon1_pt
    decay_1_eta[selection] = events[selection].muon1_eta
    decay_1_phi[selection] = events[selection].muon1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.105658)
    decay_1_pdgId[selection] = 13 * events.muon1_charge[selection]

    decay_2_pt[selection] = events[selection].tau2_pt
    decay_2_eta[selection] = events[selection].tau2_eta
    decay_2_phi[selection] = events[selection].tau2_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (1.77686)
    decay_2_pdgId[selection] = 15 * events.tau2_charge[selection]

    selection = (events.Category_pairsLoose == 2) & (events.ele1_charge * events.tau1_charge < 0)
    decay_1_pt[selection] = events[selection].ele1_pt
    decay_1_eta[selection] = events[selection].ele1_eta
    decay_1_phi[selection] = events[selection].ele1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.000511)
    decay_1_pdgId[selection] = 11 * events.ele1_charge[selection]

    decay_2_pt[selection] = events[selection].tau1_pt
    decay_2_eta[selection] = events[selection].tau1_eta
    decay_2_phi[selection] = events[selection].tau1_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (1.77686)
    decay_2_pdgId[selection] = 15 * events.tau1_charge[selection]

    selection = (events.Category_pairsLoose == 2) & (events.ele1_charge * events.tau2_charge < 0) & (events.ele1_charge * events.tau1_charge >= 0)

    decay_1_pt[selection] = events[selection].ele1_pt
    decay_1_eta[selection] = events[selection].ele1_eta
    decay_1_phi[selection] = events[selection].ele1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.000511)
    decay_1_pdgId[selection] = 11 * events.ele1_charge[selection]

    decay_2_pt[selection] = events[selection].tau2_pt
    decay_2_eta[selection] = events[selection].tau2_eta
    decay_2_phi[selection] = events[selection].tau2_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (1.77686)
    decay_2_pdgId[selection] = 15 * events.tau2_charge[selection]

    selection = events.Category_pairsLoose == 5

    decay_1_pt[selection] = events[selection].ele1_pt
    decay_1_eta[selection] = events[selection].ele1_eta
    decay_1_phi[selection] = events[selection].ele1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.000511)
    decay_1_pdgId[selection] = 11 * events.ele1_charge[selection]

    decay_2_pt[selection] = events[selection].ele2_pt
    decay_2_eta[selection] = events[selection].ele2_eta
    decay_2_phi[selection] = events[selection].ele2_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (0.000511)
    decay_2_pdgId[selection] = 11 * events.ele2_charge[selection]

    selection = events.Category_pairsLoose == 4

    decay_1_pt[selection] = events[selection].muon1_pt
    decay_1_eta[selection] = events[selection].muon1_eta
    decay_1_phi[selection] = events[selection].muon1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.105658)
    decay_1_pdgId[selection] = 13 * events.muon1_charge[selection]

    decay_2_pt[selection] = events[selection].muon2_pt
    decay_2_eta[selection] = events[selection].muon2_eta
    decay_2_phi[selection] = events[selection].muon2_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (0.105658)
    decay_2_pdgId[selection] = 13 * events.muon2_charge[selection]

    selection = (events.Category_pairsLoose == 6) & (events.muon1_charge * events.ele1_charge < 0)
    decay_1_pt[selection] = events[selection].muon1_pt
    decay_1_eta[selection] = events[selection].muon1_eta
    decay_1_phi[selection] = events[selection].muon1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.105658)
    decay_1_pdgId[selection] = 13 * events.muon1_charge[selection]

    decay_2_pt[selection] = events[selection].ele1_pt
    decay_2_eta[selection] = events[selection].ele1_eta
    decay_2_phi[selection] = events[selection].ele1_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (0.000511)
    decay_2_pdgId[selection] = 11 * events.ele1_charge[selection]


    selection = (events.Category_pairsLoose == 6) & (events.muon1_charge * events.ele2_charge < 0) & (events.muon1_charge * events.ele1_charge >= 0)

    decay_1_pt[selection] = events[selection].muon1_pt
    decay_1_eta[selection] = events[selection].muon1_eta
    decay_1_phi[selection] = events[selection].muon1_phi
    decay_1_mass[selection] = numpy.ones(len(events[selection])) * (0.105658)
    decay_1_pdgId[selection] = 13 * events.muon1_charge[selection]

    decay_2_pt[selection] = events[selection].ele2_pt
    decay_2_eta[selection] = events[selection].ele2_eta
    decay_2_phi[selection] = events[selection].ele2_phi
    decay_2_mass[selection] = numpy.ones(len(events[selection])) * (0.000511)
    decay_2_pdgId[selection] = 11 * events.ele2_charge[selection]

   # using fancy vector package for this

    decay_1_p4 = vector.awk({"pt": decay_1_pt, "eta": decay_1_eta, "phi": decay_1_phi, "mass": decay_1_mass})
    decay_2_p4 = vector.awk({"pt": decay_2_pt, "eta": decay_2_eta, "phi": decay_2_phi, "mass": decay_2_mass})

    events["decay_1_pt"] = decay_1_p4.pt
    events["decay_1_eta"] = decay_1_p4.eta
    events["decay_1_phi"] = decay_1_p4.phi
    events["decay_1_energy"] = decay_1_p4.energy
    events["decay_1_mass"] = decay_1_p4.mass
    events["decay_1_pdgId"] = decay_1_pdgId
    events["decay_2_pt"] = decay_2_p4.pt
    events["decay_2_eta"] = decay_2_p4.eta
    events["decay_2_phi"] = decay_2_p4.phi
    events["decay_2_energy"] = decay_2_p4.energy
    events["decay_2_mass"] = decay_2_p4.mass
    events["decay_2_pdgId"] = decay_2_pdgId
    events["m_tautau_vis"] = (decay_1_p4 + decay_2_p4).mass

    return events


def set_collinear_mass(events):

    # get the collinear MET values
    phi = events["MET_phi"]
    phi1 = events["decay_1_phi"]
    phi2 = events["decay_2_phi"]
    MET = events["MET"]
    denom = numpy.cos(phi1) * numpy.sin(phi2) - numpy.sin(phi1) * numpy.cos(phi2)
    MET_1 = MET * (numpy.cos(phi) * numpy.sin(phi2) - numpy.sin(phi) * numpy.cos(phi2))/denom
    MET_2 = MET * (numpy.cos(phi1) * numpy.sin(phi) - numpy.sin(phi1) * numpy.cos(phi))/denom
    x1 = events["decay_1_pt"]/(events["decay_1_pt"] + MET_1)
    x2 = events["decay_2_pt"]/(events["decay_2_pt"] + MET_2)
    events["m_tautau_collinear"] = events["m_tautau_vis"]/(numpy.sqrt(x1 * x2))
    return events


@numba.njit
def mapMotherToDaughter(goodMotherIndices, allMotherIndices):
    """Finds the indices of the daughters such that the mothers are a part of the goodMotherIndices array
Will be used to find the taus (among many taus) whose mothers are the good Z/H bosons"""
    a = numpy.ones(len(goodMotherIndices)) * -1
    for i in range((len(goodMotherIndices))):
        if len(goodMotherIndices[i]) > 0:
            for j in range(len(allMotherIndices[i])):
                if goodMotherIndices[i][0] == allMotherIndices[i][j]:
                    a[i] = j
    return a


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
        if numpy.isnan(cosTheta[i]):
            print(parent.pt, daughter.pt)
    return cosTheta
