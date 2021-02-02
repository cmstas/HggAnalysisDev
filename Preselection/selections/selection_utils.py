import numpy

class CutDiagnostics():
    def __init__(self, **kwargs):
        self.n_events_initial = kwargs.get("n_events_initial")
        self.debug = kwargs.get("debug")
        self.cut_set = kwargs.get("cut_set", "cut")
        self.cuts = [float(self.n_events_initial)]

        if self.debug:
            print("%s CutDiagnostics: %d events before any cuts" % (self.cut_set, self.n_events_initial)) 

    #TODO: add way to keep track of object-level cuts
    #def add_object_cut(self, objects)

    def add_cut(self, n_events, cut_name = "cut"):
        self.cuts.append(float(n_events))
        if self.debug:
            print("%s CutDiagnostics: After cut %s, %d events (eff_cut: %.4f, eff_total: %.4f)" % (self.cut_set, cut_name, n_events, self.cuts[-1] / self.cuts[-2], self.cuts[-1] / self.cuts[0])) 


def convert_object_cuts_to_listOffset(object_cuts):
    """
    Takes as input an awkward array of bools (True = keep object, False = cut object)
    and transforms it to an awkward ListOffsetArray so that events can be cut
    """

    nEvents = len(object_cuts)
    nObjects = numpy.int64(0)

    for i in range(nEvents):
        nObjects += len(object_cuts[i])

    mask_offsets = numpy.empty(nEvents + 1, numpy.int64)
    mask_offsets[0] = 0
    mask_contents = numpy.empty(nObjects, numpy.bool)

    for i in range(nEvents):
        mask_offsets[i+1] = mask_offsets[i]
    
    return
