import numpy
import awkward
import vector

class CutDiagnostics():
    def __init__(self, **kwargs):
        self.debug = kwargs.get("debug")
        self.cut_set = kwargs.get("cut_set", "cut")
        self.events = kwargs.get("events")

        self.n_events_initial = len(self.events)

    def add_cuts(self, cuts, names): 
        for cut, name in zip(cuts, names):
            if self.debug > 0:
                n_events_cut = len(self.events[cut])
                if self.n_events_initial == 0:
                    return
                print("%s EventCutDiagnostics: Cut %s has an eff of %.4f" % (self.cut_set, name, float(n_events_cut) / float(self.n_events_initial)))

class ObjectCutDiagnostics():
    def __init__(self, **kwargs):
        self.objects = kwargs.get("objects")
        self.debug = kwargs.get("debug")
        self.cut_set = kwargs.get("cut_set", "cut")

        self.n_objects_initial = awkward.sum(awkward.num(self.objects))

    def add_cuts(self, cuts, names):
        for cut, name in zip(cuts, names):
            if self.debug > 0:
                n_objects_cut = awkward.sum(awkward.num(self.objects[cut]))
                if self.n_objects_initial == 0:
                    return
                print("%s ObjectCutDiagnostics: Applying cut %s would have an eff of %.4f" % (self.cut_set, name, float(n_objects_cut) / float(self.n_objects_initial)))

def pad_awkward_array(array, pad_length, pad_value):
    return awkward.fill_none(awkward.pad_none(array, pad_length, clip=True), pad_value)

def items2vectors(events,names):
    vectors = []
    if "selectedPhoton" in names:
        vectors.append(
            vector.obj(
                pt = events['selectedPhoton_pt'],
                eta = events['selectedPhoton_eta'],
                phi = events['selectedPhoton_phi'],
                M = events['selectedPhoton_mass']
            )
        )
    if "FatJet" in names:
        vectors.append(
            vector.obj(
                pt = events['FatJet_pt'],  
                eta = events['FatJet_eta'],
                phi = events['FatJet_phi'],
                M = events['FatJet_msoftdrop']
            )
        )
    return vectors


def items2vector(item,softDrop=False):
    
    if softDrop: 
        mass = item.msoftdrop
    else: 
        mass = item.mass
    p4 = vector.arr(
        {
            "pt" : item.pt,
            "eta" : item.eta,
            "phi" : item.phi,
            "M" : mass
        }
        )
        
    return p4


def items2akvector(item, softDrop=False):

    if softDrop:
        mass = item.msoftdrop
    else:
        mass = item.mass
    p4 = vector.awk(
        {
            "pt": item.pt,
            "eta": item.eta,
            "phi": item.phi,
            "M": mass
        }
    )

    return p4


def components2vector(item_pt,item_eta,item_phi,item_mass):

    p4 = vector.arr(
        {
            "pt": item_pt,
            "eta": item_eta,
            "phi": item_phi,
            "M": item_mass
        }
    )

    return p4
    
