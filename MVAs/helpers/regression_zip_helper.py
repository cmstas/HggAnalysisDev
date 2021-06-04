import h5py
import pandas
import numpy
import json

from helpers import mva_helper, regression_nn_helper, utils

class ZipHelper():
    """
    Class to take an input ntuple and one or more MVAs,
    evaluate the MVA scores for each event and then write
    an output ntuple with the MVA scores and a subset of
    branches from the original ntuple
    """
    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.mva_files = kwargs.get("mvas")
        self.names = kwargs.get("names")
        self.debug = kwargs.get("debug")
        self.output = kwargs.get("output")

        if self.debug > 0:
            print("[ZipHelper] Creating Regression ZipHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        self.df = pandas.read_pickle(self.input)
        if self.debug > 0:
             print("[ZipHelper] Loaded file %s, containing %d events" % (self.input, len(self.df)))

    def run(self):
        self.load_mvas()
        self.calculate_scores()
        self.save_df


    def load_mvas(self):
        self.mvas = {}
        self.mva_configs = {}
        self.mva_files = self.mva_files.split(",")
        self.names = self.names.split(",")
        for name, file in zip(self.names, self.mva_files):
            with open(file, "r") as f_in:
                self.mva_configs[name] = json.load(f_in)

        for name, config in self.mva_configs.items():
            if config["config"]["mva"]["type"] == "regression_neural_network":
                nn = regression_nn_helper.NNHelper(
                    events = None,
                    config = self.config,
                    output_tag = self.output_tag,
                    debug = self.debug
                    )
                self.mvas[name] = nn

    def calculate_scores(self):
        for name, mva in self.mvas.items():
            scores = mva.predict_from_df(self.df)
            self.df[name] = scores

    def save_df(self):
        self.df.to_pickle(self.output)

