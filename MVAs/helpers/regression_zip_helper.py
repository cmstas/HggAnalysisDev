import h5py
import pandas
import numpy
import json
import os
from helpers import mva_helper, regression_nn_helper, utils
from sklearn.preprocessing import StandardScaler
import pickle as pkl 

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
        self.scaler_file = kwargs.get("scaler_file")
        if self.debug > 0:
            print("[ZipHelper] Creating Regression ZipHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        self.df = pandas.read_pickle(self.input)
        if self.debug > 0:
             print("[ZipHelper] Loaded file %s, containing %d events" % (self.input, len(self.df)))

    def run(self):
        self.load_and_calculate_mvas()
#        self.calculate_scores()
        self.save_df()


    def load_and_calculate_mvas(self):
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
                    config = None,
                    output_tag = config["config"]["mva"]["model_file"],
                    debug = self.debug
                    )
                nn.load_model("best")
                self.mvas[name] = nn
                # Load standard scaler
                numeric_columns = [i for i in config["config"]["mva"]["training_features"] if "onehot" not in i and "jet" not in i]

                if self.scaler_file and "standard_scaling" in config["config"]["mva"].keys() and config["config"]["mva"]["standard_scaling"]:
                    self.scaler = pkl.load(open(self.scaler_file, "rb"))
                    if type(self.scaler) is not dict:
                        self.df[numeric_columns] = self.scaler.transform(self.df[numeric_columns])
                    else: # elaborate gymnastics to accommodate jet1 and jet2
                        for name, scaler in self.scaler.items():
                            if "jet" in name:
                                jet_features = [i for i in config["config"]["mva"]["training_features"] if name in i]
                                pt_variable = [i for i in jet_features if "pt" in i][0]
                                self.df.loc[self.df[pt_variable] > 0, jet_features] = scaler.transform(self.df.loc[self.df[pt_variable] > 0, jet_features])
                            else:
                                self.df[numeric_columns] = self.scaler.transform(self.df[numeric_columns]) 

                scores = nn.predict_from_df(self.df, config["config"]["mva"]["training_features"])
                self.df[name] = scores["inference"]
                if self.scaler_file and "standard_scaling" in config["config"]["mva"].keys() and config["config"]["mva"]["standard_scaling"]:
                    self.df[numeric_columns] = self.scaler.inverse_transform(self.df[numeric_columns])
                   

                
    def calculate_scores(self):
        for name, mva in self.mvas.items():
            config = self.mva_configs[name]
            scores = mva.predict_from_df(self.df, config["config"]["mva"]["training_features"])
            self.df[name] = scores["inference"]
            # unscale
            numeric_columns = [i for i in config["config"]["mva"]["training_features"] if "onehot" not in i and "jet" not in i]
            if type(self.scaler) is not dict:
                self.df[numeric_columns] = self.scaler.inverse_transform(self.df[numeric_columns])
            else:
                for name, scaler in self.scaler.items():
                    if "jet" in name:
                        jet_features = [i for i in config["config"]["mva"]["training_features"] if name in i]
                        pt_variable = [i for i in jet_features if "pt" in i][0]
                        self.df.loc[self.df[pt_variable] > 0, jet_features] = scaler.inverse_transform(self.df.loc[self.df[pt_variable] > 0, jet_features])
                    else:
                            self.df[numeric_columns] = self.scaler.inverse_transform(self.df[numeric_columns]) 


    def save_df(self):
        self.df.to_pickle(self.output)

