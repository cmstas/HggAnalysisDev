import json

class LoopHelper():
    """
    Class to perform all looping activities: looping through samples,
    filling histograms, making data/MC plots, yield tables,
    writing a single ntuple with all events, etc
    """

    def __init__(self, **kwargs):
        self.samples = kwargs.get("samples")
        self.selections = kwargs.get("selections")
        self.options = kwargs.get("options")
        self.systematics = kwargs.get("systematics")
        
        self.output_tag = kwargs.get("output_tag")
        
        self.batch = kwargs.get("batch")
        self.nCores = kwargs.get("nCores")
        self.debug = kwargs.get("debug")

        self.do_plots = kwargs.get("do_plots")
        self.do_tables = kwargs.get("do_tables")
        self.do_ntuple = kwargs.get("do_ntuple")

        if self.debug > 0:
            print("[LoopHelper] Creating LoopHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        self.load_samples()

    def load_samples(self):
        with open(self.samples, "r") as f_in:
            self.samples_dict = json.load(f_in)

        if self.debug > 0:
            print("[LoopHelper] Running over the following samples:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in self.samples_dict.items()]))

    def run(self):
        for sample, info in self.samples_dict.items():
            if self.debug > 0:
                print("[LoopHelper] Running over sample: %s" % sample)
                print("[LoopHelper] details: ", info)

            self.loop_sample(sample, info)

    def loop_sample(self, sample, info):
        return
