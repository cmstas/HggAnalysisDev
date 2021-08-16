import awkward
import numpy
import vector

import selections.selection_utils as utils
import selections.object_selections as object_selections

# import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

# call("mkdir -p logs", shell=True)
# #file_handler = logging.FileHandler('logs/processor.log')
# file_handler = logging.FileHandler('processor.log')
# file_handler.setFormatter(formatter)

# logger.addHandler(file_handler)

def pvec(vec4):
  vec3 = vector.obj(
    x=vec4.x,
    y=vec4.y,
    z=vec4.z
  )
  return vec3

def getcosthetastar_cs(diphoton, fatjet):

    # https://github.com/cms-analysis/flashgg/blob/1453740b1e4adc7184d5d8aa8a981bdb6b2e5f8e/DataFormats/src/DoubleHTag.cc#L41
    beam_energy = 6500
    nevts = len(diphoton)
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

    #  ___________________ 
    # |        ___        |
    # |  /^^^\{6,6}/^^^\  |
    # |  \^^^/(""")\^^^/  |
    # |  /^^/  \"/  \^^\  |
    # | /'`    /|\    `'\ |
    # |___________________|
    #                  
           
    ## check nan  
    hh = diphoton + fatjet
    boostvec = hh.to_beta3() * -1

    p1_boost = p1.boost(boostvec)
    p2_boost = p2.boost(boostvec)
 
    # pvec.unit == to_beta3().unit()?
    CSaxis = (pvec(p1_boost).unit() - pvec(p2_boost).unit()).unit()
    diphoton_vec_unit = diphoton.to_beta3().unit()

    # logger.debug(f"{p1_boost[0].to_list()}")
    # logger.debug(f"{pvec(p1_boost)[0]}")
    # logger.debug(f"{diphoton[0].to_list()}")
    # logger.debug(f"{pvec(diphoton)[0]}")

    return CSaxis.dot(diphoton_vec_unit)

def helicityCosTheta(booster, boosted):
    # https://github.com/cms-analysis/flashgg/blob/1453740b1e4adc7184d5d8aa8a981bdb6b2e5f8e/DataFormats/src/DoubleHTag.cc#L93
    ## both inputs are Lorentz vector

    boostVector = pvec(booster)
    boosted.boost(-1*boostVector)

    return np.cos(boosted.theta)


def set_helicity(events, photons, fatjets, options, debug):
    # FIXME I need to build the diphoton 4vector and the fatjet one 
    diphoton = photons[:,0] + photons[:,1]
    
    events["costhetastar_cs"] = getcosthetastar_cs(diphoton, fatjet) 
    events["costheta_gg"] = helicityCosTheta(diphoton, photons[:,0])
    events["costheta_bb"] = helicityCosTheta(diphoton, fatjets[:,0])
                   
    return events


