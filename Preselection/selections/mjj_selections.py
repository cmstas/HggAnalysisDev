import awkward as ak

import selections.selection_utils as utils
import selections.object_selections as object_selections
        # 1 find best tagged fatjet
        # 2 use the nearest function
        # 3 use the inv mass function

def mjj_filter(events, fatjets, jets, mjj_range, debug):
        
  fatjets.Tbb = fatjets.particleNetMD_Xbb / \
    (1 - fatjets.particleNetMD_Xqq - fatjets.particleNetMD_Xcc)
  fatjet = fatjets[ak.argmax(fatjets.Tbb,axis=1,keepdims=True)]
  print ("best fatjet eta {} and jet eta {}".format(fatjet.eta,fatjet.phi))
  match_mask = object_selections.mask_nearest(ak.flatten(fatjet.eta),ak.flatten(fatjet.phi),jets.eta,jets.phi,threshold=0.4)
  matched_jet = jets[match_mask]
  other_jets = jets[~match_mask]
  mjj_cut = object_selections.select_mass(events,matched_jet,other_jets,mjj_range,debug)
  selected_events = events[mjj_cut]
    
  return selected_events     


# def mjj_filter_basic(events, jets, mjj_range, options debug):

#   jets.btagDeepFlavB
#   fatjet = fatjets[awkward.argmax(fatjets.Tbb)]
#   match_mask = object_selections.mask_nearest()
#   matched_jet = jets[]
#   selected_events = events[mjj_cut]

#   return selected_events
