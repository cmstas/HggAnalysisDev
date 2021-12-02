import awkward as ak
import numpy as np
import vector

import selections.object_selections as object_selections
import selections.selection_utils as utils


def pvec(vec4):
  vec3 = vector.obj(
    x=vec4.x,
    y=vec4.y,
    z=vec4.z
  )
  return vec3

def getcosthetastar_cs(events,diphoton, fatjet):

    print ("\n\n Hgg is {} and Hxx is {}".format(diphoton, fatjet))
    # https://github.com/cms-analysis/flashgg/blob/1453740b1e4adc7184d5d8aa8a981bdb6b2e5f8e/DataFormats/src/DoubleHTag.cc#L41
    beam_energy = 6500
    nevts = len(events)
    costhetastar_cs = np.ones(nevts)*-999 # is it needed?

    # convert using vector
    p1 = vector.obj(
          x=np.zeros(nevts),
          y=np.zeros(nevts),
          z=np.ones(nevts)*beam_energy,
          t=np.ones(nevts)*beam_energy,
        )

    p2 = vector.obj(
          x=np.zeros(nevts),
          y=np.zeros(nevts),
          z=np.ones(nevts)*beam_energy*(-1),
          t=np.ones(nevts)*beam_energy,
        )
           
    hh = diphoton + fatjet
    boostvec = hh.to_beta3() * -1

    p1_boost = p1.boost(boostvec)
    p2_boost = p2.boost(boostvec)

    CSaxis = (pvec(p1_boost).unit() - pvec(p2_boost).unit()).unit()
    
    diphoton_boost = diphoton.boost(boostvec)
    diphoton_vec_unit = pvec(diphoton_boost).unit()


    return CSaxis.dot(diphoton_vec_unit)

def helicityCosTheta(booster, boosted):
    # https://github.com/cms-analysis/flashgg/blob/1453740b1e4adc7184d5d8aa8a981bdb6b2e5f8e/DataFormats/src/DoubleHTag.cc#L93
    ## both inputs are Lorentz vector

    boostVector = pvec(booster)
    boosted.boost(-1*boostVector)

    return np.cos(boosted.theta)


def set_helicity(events,photons, fatjets, bjets, options, debug):
    
    photon1_p4 = utils.items2vector(photons[:,0])
    photon2_p4 = utils.items2vector(photons[:,1])
    fatjets_p4 = utils.items2akvector(fatjets, softDrop=True)
    
    diphoton = photon1_p4 + photon2_p4
    
    n_save = 3 #Hardcoded same number of saved fatjets

    costhetastar_padded = utils.pad_awkward_array(abs(getcosthetastar_cs(events, diphoton, fatjets_p4)),n_save,-9)
    dphi_gg_fj_padded = utils.pad_awkward_array(object_selections.d_phi(diphoton.phi,fatjets_p4.phi) ,n_save, -9)
    
    # TODO costheta_bb still to be implemented
    # bjet_padded_eta = utils.pad_awkward_array(bjets.eta,n_save,-9)
    # bjet_padded_phi = utils.pad_awkward_array(bjets.phi,n_save,-9)
    for i in range(n_save):
      events["costhetastar_cs_%s" % str(i+1)] = costhetastar_padded[:,i]
      events["diphoton_fatjet%s_dphi" % str(i+1)] = dphi_gg_fj_padded[:,i]

      #find closest bjet TODO
      # closest_bjet_mask = object_selections.mask_nearest(
      #     fatjet_padded_eta[:, i], fatjet_padded_phi[:, i], bjet_padded_eta, bjet_padded_phi, threshold=0.4)
      # subjet = bjet[closest_bjet_mask]
      # subjet_p4 = utils.items2vector(subjet)
      # events["costheta_bb_%s"% str(i+1)] = abs(helicityCosTheta(fatjet_p4, subjet_p4))
    
    events["costheta_gg"] = abs(helicityCosTheta(diphoton, photon1_p4) )
                   
    return events


