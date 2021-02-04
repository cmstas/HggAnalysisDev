import numpy
import awkward

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
