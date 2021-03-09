import hepstats

from helpers import model_helper

class FitHelper()
    """
    Class to take an arbitrary number of parametric models for both signal and background
    and calculate a specified metric (Asymptotic upper limit, significance, etc)
    """

    def __init__(self, **kwargs):
        self.signals = kwargs.get("signals")
        self.backgrounds = kwargs.get("backgrounds")
        self.debug = kwargs.get("debug")
        self.output_tag = kwargs.get("output_tag")
        self.options = kwargs.get("options")

