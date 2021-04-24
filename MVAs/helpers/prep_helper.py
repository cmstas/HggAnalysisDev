import h5py
import pandas
import json
import numpy as np
import random

from helpers import utils

class PrepHelper():
    """
    Class to read events in from an ntuple and perform necessary
    preprocessing, sample labeling, etc and then write them
    to an output hdf5 file to be used for BDT/DNN training
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.output = kwargs.get("output")
        self.debug = kwargs.get("debug")
        self.config_file = kwargs.get("config")

        if self.debug > 0:
            print("[PrepHelper] Creating PrepHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        with open(self.input.replace(".pkl", ".json"), "r") as f_in:
            self.input_config = json.load(f_in)
        self.make_process_id_map()

        with open(self.config_file, "r") as f_in:
            self.config = json.load(f_in)

        self.df = pandas.read_pickle(self.input)
        if self.debug > 0:
            print("[PrepHelper] Loaded file %s, containing %d events" % (self.input, len(self.df)))

    def run(self):
        self.prepare_samples()    
        self.preprocess() # scale sig/bkg yields, preprocess individual features, etc
        self.prepare_features()
        self.make_train_test_validation_split()
        self.write_hdf5()
        return



    def apply_preselections(self):
        if "preselections" in self.config.keys():
            if self.debug > 0:
                print("[PrepHelper] applying preselections")
            preselections = self.config["preselections"]
            VH_process_id = self.process_id_map["VH"]
            if "positive_svfit" in preselections.keys() and preselections["positive_svfit"]:
                if "m_tautauSVFitLoose" in self.df.columns:
                    self.df = self.df.loc[self.df["m_tautauSVFitLoose"] >= 0]
           
            if "Z_tauOnly" in preselections.keys() and preselections["Z_tauOnly"]:
                if "genZ_decayMode" in self.df.columns:
                    self.df = self.df.loc[((self.df["genZ_decayMode"] == 3) & (self.df["process_id"] == VH_process_id)) | ~(self.df["process_id"] == VH_process_id)]
        self.df["weight"] *= 100

        if self.debug > 0:
            print("[PrepHelper] After preselections, dataframe contains %d events" %(len(self.df)))

    def make_process_id_map(self):
        self.process_id_map = {}
        for sample, info in self.input_config["samples_dict"].items():
            self.process_id_map[sample] = info["process_id"]

        if self.debug > 0:
            print("[PrepHelper] process_id map: ", self.process_id_map)
        return

    def preprocess(self):
        if self.config["preprocess"]["scale_signal"]: # scale signal yield to bkg yield
            self.df.loc[self.df["label"] == 1, "weight"] *= self.n_background_weighted / self.n_signal_weighted
            self.n_signal_reweighted = self.df["weight"][self.df["label"] == 1].sum()

            if self.debug > 0:
                print("[PrepHelper] After scaling signal yield, total weighted signal/background events are %.6f/%.6f" % (self.n_signal_reweighted, self.n_background_weighted))

        #TODO: add options for feature preprocessing, scaling up resonant backgrounds, etc
        return

    def prepare_samples(self):
        """
        Select only the needed samples from the dataframe,
        then assign labels to signals/backgrounds
        """
        self.process_ids = []
        for process in self.config["signal"] + self.config["background"]:
           self.process_ids.append(self.process_id_map[process])

        self.df = self.df[self.df["process_id"].isin(self.process_ids)]

        #applying preselections
        self.apply_preselections()

        if self.debug > 0:
            print("[PrepHelper] After selecting for signals and backgrounds, dataframe contains %d events" % (len(self.df)))

        label = list(np.zeros(len(self.df)))
        
        self.df["label"] = label
        self.df = self.df.reset_index(drop = True) # reassign indices so we can do test/train/val splits more easily later

        # Assign signal events label of 1
        for process in self.config["signal"]:
            self.df.loc[self.df["process_id"] == self.process_id_map[process], "label"] = 1 

        self.n_signal = len(self.df[self.df["label"] == 1])
        self.n_signal_weighted = self.df["weight"][self.df["label"] == 1].sum()

        self.n_background = len(self.df[self.df["label"] == 0])
        self.n_background_weighted = self.df["weight"][self.df["label"] == 0].sum() 

        if self.debug > 0:
            print("[PrepHelper] After labeling, have %d signal events (%.6f weighted) and %d background events (%.6f weighted)" % (self.n_signal, self.n_signal_weighted, self.n_background, self.n_background_weighted))

        return

    def prepare_features(self):
        self.X = self.df[self.config["training_features"]]
        self.y = self.df["label"]
        self.weight = self.df["weight"]

    def make_train_test_validation_split(self):
        """
        In order to have a consistent way of identifying test/train/validation events
        in multiple places throughout the workflow (training MVAs, zipping MVA score back 
        into dataframe, optimizing SRs), use the following convention:
        To assign an event to test/train/val, take the decimal digits of its mgg value.
        E.g. 125.342682 -> 342682
            digits % 3 == 0 : train
            digits % 3 == 1 : test
            digits % 3 == 2 : validation

        Different test/train splits can be selected later in training for e.g. 
        optimizing hyperparameters, but this ensures consistency in knowing what is
        train/test/validation throughout the workflow
        """

        self.df, idx_train, idx_test, idx_validation = utils.make_train_test_validation_split(self.df)

        self.X_train = self.X.iloc[idx_train]
        self.y_train = self.y.iloc[idx_train]
        self.weight_train = self.weight.iloc[idx_train]
        self.X_test = self.X.iloc[idx_test]
        self.y_test = self.y.iloc[idx_test]
        self.weight_test = self.weight.iloc[idx_test]
        self.X_validation = self.X.iloc[idx_validation]
        self.y_validation = self.y.iloc[idx_validation] 
        self.weight_validation = self.weight.iloc[idx_validation]

        self.df.iloc[idx_train, self.df.columns.get_loc("train_label")] = 0
        self.df.iloc[idx_test, self.df.columns.get_loc("train_label")] = 1
        self.df.iloc[idx_validation, self.df.columns.get_loc("train_label")] = 2

        self.n_train = len(self.df[self.df["train_label"] == 0])
        self.n_test = len(self.df[self.df["train_label"] == 1])
        self.n_validation = len(self.df[self.df["train_label"] == 2])

        if self.debug > 0:
            print("[PrepHelper] Have %d/%d/%d events in train/test/validation splits" % (self.n_train, self.n_test, self.n_validation))

        return

    def write_hdf5(self):
        self.X_train.to_hdf(self.output, "X_train")
        self.y_train.to_hdf(self.output, "y_train")
        self.weight_train.to_hdf(self.output, "weight_train")
        self.X_test.to_hdf(self.output, "X_test")
        self.y_test.to_hdf(self.output, "y_test")
        self.weight_test.to_hdf(self.output, "weight_test")

        return 
