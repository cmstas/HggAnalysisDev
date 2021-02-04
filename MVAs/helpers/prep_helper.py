import h5py
import pandas
import json

class PrepHelper():
    """
    Class to read events in from an ntuple and perform necessary
    preprocessing, sample labeling, etc and then write them
    to an output hdf5 file to be used for BDT/DNN trainig
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.output = kwargs.get("output")
        self.debug = kwargs.get("debug")
        self.config_file = kwargs.get("config")

        if self.debug > 0:
            print("[PrepHelper] Creating PrepHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        with open(self.config_file, "r") as f_in:
            self.config = json.load(f_in)

        self.df = pandas.read_pickle(self.input)
        
    def run(self):
        
        return

