import numpy

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
            print("%s CutDiagnostics: After cut %s, %d events (eff_cut: %.4f, eff_total: %.4f)" % (self.cut_set, cut_name, n_events, self.cuts[-1] / self.cuts[-2], self.cuts[-1] / self.cuts[0])) 

