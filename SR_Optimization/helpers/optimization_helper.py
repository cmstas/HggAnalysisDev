import pandas

class OptimizationHelper():
    """
    Class to take an input ntuple with MVA scores and optimize cuts
    on MVA scores in order to maximize expected sensitivity for some
    metric (significance, upper limit, etc)
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.debug = kwargs.get("debug")
        self.output_tag = kwargs.get("output_tag")
        self.optimization_options = kwargs.get("optimization_options")
        self.metric = kwargs.get("metric")

        self.batch = kwargs.get("batch")
        self.nCores = kwargs.get("nCores")

        if self.debug > 0:
            print("[OptimizationHelper] Creating OptimizationHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        self.events = pandas.read_pickle(self.input)

        if self.debug > 0:
            print("[OptimizationHelper] Loaded dataframe from file %s with %d events" % (self.input, len(self.events)))

    def run(self):
        return
