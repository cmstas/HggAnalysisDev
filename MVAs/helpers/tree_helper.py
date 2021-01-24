import h5py
from . import utils

class TreeHelper():
    """
    Class to take an input ntuple and one or more MVAs,
    evaluate the MVA scores for each event and then write
    an output ntuple with the MVA scores and a subset of
    branches from the original ntuple
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.mvas = kwargs.get("mvas")
        self.branches = kwargs.get("branches")
        self.debug = kwargs.get("debug")
        self.output = kwargs.get("output")

        if self.debug > 0:
            print("[TreeHelper] Creating TreeHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

    def run(self):
        return
