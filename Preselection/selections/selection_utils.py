import numpy
import awkward

class CutDiagnostics():
    def __init__(self, **kwargs):
        self.n_events_initial = kwargs.get("n_events_initial")
        self.debug = kwargs.get("debug")
        self.cut_set = kwargs.get("cut_set", "cut")
        self.cuts = [float(self.n_events_initial)]

        if self.debug:
            print("%s CutDiagnostics: %d events before any cuts" % (self.cut_set, self.n_events_initial)) 

    def add_cut(self, n_events, cut_name = "cut"):
        self.cuts.append(float(n_events))
        if self.debug:
            if n_events == 0 or self.cuts[-2] == 0:
                return
            print("%s CutDiagnostics: After cut %s, %d events (eff_cut: %.4f, eff_total: %.4f)" % (self.cut_set, cut_name, n_events, self.cuts[-1] / self.cuts[-2], self.cuts[-1] / self.cuts[0])) 

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
