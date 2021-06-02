import h5py
import pandas
import json
import numpy as np
import random

from helpers import utils

class RegressionPrepHelper():
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
            print("[PrepHelper] Creating Regression PrepHelper instance with options:")
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
        self.make_train_test_validation_split() # shuffling happens here
        self.write_hdf5()
        return

    def make_train_test_validation_split(self):
        # mark events as train/val/test - 75% train, 15% val, 10% test
        # Then shuffle the events to mix the masses

        gen_higgs_masses = self.df["gen_higgs_mass"].unique()
        idx_train = None
        idx_validation = None
        idx_test =None
        for mass in gen_higgs_masses:
            tempDF = self.df.loc[df["gen_higgs_mass"] == mass]
            tempIndices = tempDF.index
            if idx_train is None:
                idx_train = tempIndices[:int(0.75 * len(tempDF))]
                idx_test = tempIndices[int(0.75 * len(tempDF)):int(0.9 * len(tempDF))]
                idx_validation = tempIndices[int(0.9 * len(tempDF)):]
            else:
                idx_train = idx_train.append(tempIndices[:int(0.75 * len(tempDF))])
                idx_test = idx_test.append(tempIndices[int(0.75 * len(tempDF)):int(0.9 * len(tempDF))])
                idx_validation = idx_validation.append(tempIndices[int(0.9 * len(tempDF)):])

        self.df.iloc[idx_train, self.df.columns.get_loc("train_label")] = 0
        self.df.iloc[idx_test, self.df.columns.get_loc("train_label")] = 1
        self.df.iloc[idx_validation, self.df.columns.get_loc("train_label")] = 2

        # shuffle here
        self.df_train = self.df.iloc[idx_train].copy()
        self.df_val = self.df.iloc[idx_validation].copy()
        self.df_test = self.df.iloc[idx_test].copy()

        self.df_train = self.df_train.sample(frac=1).reset_index(drop=True)
        self.df_val = self.df_val.sample(frac=1).reset_index(drop=True)
        self.df_test = self.df_test.sample(frac=1).reset_index(drop=True)

        self.X_train = self.df_train[self.config["training_features"]]
        self.y_train = self.df_train["gen_higgs_mass"]

        self.X_val = self.df_val[self.config["training_features"]]
        self.y_val = self.df_val["gen_higgs_mass"]

        self.X_test = self.df_test[self.config["training_features"]]
        self.y_test = self.df_test["gen_higgs_mass"]

        self.n_train = len(self.df[self.df["train_label"] == 0])
        self.n_test = len(self.df[self.df["train_label"] == 1])
        self.n_validation = len(self.df[self.df["train_label"] == 2])

    def write_hdf5(self):
        self.X_train.to_hdf(self.output, "X_train")
        self.y_train.to_hdf(self.output, "y_train")
        self.X_test.to_hdf(self.output, "X_test")
        self.y_test.to_hdf(self.output, "y_test")

        df_output_name = self.input[:-4] + "_with_labels.pkl"
        self.df.to_pickle(df_output_name)
