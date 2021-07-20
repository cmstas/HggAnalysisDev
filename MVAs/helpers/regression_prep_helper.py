import h5py
import pandas
import json
import numpy as np
import random
from sklearn.preprocessing import StandardScaler
from helpers import utils
import pickle as pkl

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
            print("[PrepHelper] Creating Regression PrepHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        with open(self.input.replace(".pkl", ".json"), "r") as f_in:
            self.input_config = json.load(f_in)

        with open(self.config_file, "r") as f_in:
            self.config = json.load(f_in)

        self.df = pandas.read_pickle(self.input)
        if self.debug > 0:
            print("[PrepHelper] Loaded file %s, containing %d events" % (self.input, len(self.df)))

    def run(self):
        self.preprocess()
        self.make_train_test_validation_split() # shuffling happens here
        self.scale_variables()
        self.write_hdf5()
        return

    def preprocess(self):
        # eliminate -1 category
        self.df = self.df.loc[self.df["Category_pairsLoose"] != -1].reset_index(drop=True)
#        self.df["gen_higgs_mass"] = round(self.df["gen_higgs_mass"])
#        self.df = self.df.loc[self.df["gen_higgs_mass"] % 5 == 0].reset_index(drop=True)
#        self.df = self.df.loc[self.df["gen_higgs_mass"] == self.df["gen_higgs_mass"].astype(np.int32)].reset_index(drop=True)
        # restrict mass
        if "restrict_mass" in self.config.keys() and self.config["restrict_mass"]:
            if self.debug > 0:
                print("[PrepHelper] restricting mass to 110 GeV")
            self.df = self.df.loc[self.df["gen_higgs_mass"] <= 110].reset_index(drop=True)

        if "Category_onehot_1" not in self.df.columns:
            for i in range(1,6):
                self.df["Category_onehot_{}".format(i)] = np.zeros(len(self.df))

            for i in range(2,7):
                self.df.loc[self.df["Category_pairsLoose"] == i,"Category_onehot_{}".format(i-1)] = 1

        # Normalize the pt features and the mass features
        if "normalize_with_visible_tau_mass" in self.config.keys() and self.config["normalize_with_visible_tau_mass"]:
            normalizable_features = [i for i in self.config["training_features"] if "pt" in i or "mass" in i or "MET_cov" in i]
            if self.debug > 0:
                print("[PrepHelper] Normalizable features = ", normalizable_features)
            for column in normalizable_features:
                if "MET_cov" in column:
                    self.df[column] /= (self.df["m_tautau_vis"] ** 2)
                else:
                    self.df[column] /= self.df["m_tautau_vis"]
            self.df["gen_higgs_mass_normalized"] = self.df["gen_higgs_mass"] / self.df["m_tautau_vis"]
            # MEGA SCALING
            self.df = self.df.loc[self.df["gen_higgs_mass_normalized"] < 5].reset_index(drop=True)
            self.target = "gen_higgs_mass_normalized"
        else:
            self.target = "gen_higgs_mass"
        # taking log of variables
        if "log_features" in self.config.keys():
            log_variables = self.config["log_features"]
            if self.debug > 0:
                print("[PrepHelper] log transform the following features")
                print(log_variables)
            for column in log_variables:
                self.df[column] = np.log(self.df[column])

    def make_train_test_validation_split(self):
        indices = np.random.permutation(self.df.index)
        train_idx = indices[:int(0.65 * len(indices))]
        val_idx = indices[int(0.65 * len(indices)):int(0.9 * len(indices))]
        test_idx = indices[int(0.9 * len(indices)):]

        self.df["train_label"] = np.zeros(len(self.df))
        self.df.iloc[train_idx, self.df.columns.get_loc("train_label")] = 0
        self.df.iloc[val_idx, self.df.columns.get_loc("train_label")] = 1
        self.df.iloc[test_idx, self.df.columns.get_loc("train_label")] = 2

        # shuffle here
        self.df_train = self.df.iloc[train_idx].copy()
        self.df_val = self.df.iloc[val_idx].copy()
        self.df_test = self.df.iloc[test_idx].copy()

    def make_train_test_validation_split_gen_higgs(self):
        # mark events as train/val/test - 75% train, 15% val, 10% test
        # Then shuffle the events to mix the masses

        gen_higgs_masses = self.df["gen_higgs_mass"].unique()
        idx_train = None
        idx_validation = None
        idx_test =None
        for mass in gen_higgs_masses:
            tempDF = self.df.loc[self.df["gen_higgs_mass"] == mass]
            tempIndices = tempDF.index
            if idx_train is None:
                idx_train = tempIndices[:int(0.65 * len(tempDF))]
                idx_test = tempIndices[int(0.65 * len(tempDF)):int(0.9 * len(tempDF))]
                idx_validation = tempIndices[int(0.9 * len(tempDF)):]
            else:
                idx_train = idx_train.append(tempIndices[:int(0.65 * len(tempDF))])
                idx_test = idx_test.append(tempIndices[int(0.65 * len(tempDF)):int(0.9 * len(tempDF))])
                idx_validation = idx_validation.append(tempIndices[int(0.9 * len(tempDF)):])

        self.df["train_label"] = np.zeros(len(self.df))
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

        # add event weights
        for higgsMass in self.df_train["gen_higgs_mass"].unique():
            self.df_train.loc[self.df_train["gen_higgs_mass"] == higgsMass, "weight"] = 1000.0/len(self.df_train.loc[self.df_train["gen_higgs_mass"] == higgsMass])


        for higgsMass in self.df_val["gen_higgs_mass"].unique():
            self.df_val.loc[self.df_val["gen_higgs_mass"] == higgsMass, "weight"] = 1000.0/len(self.df_val.loc[self.df_val["gen_higgs_mass"] == higgsMass])

        for higgsMass in self.df_test["gen_higgs_mass"].unique():
            self.df_test.loc[self.df_test["gen_higgs_mass"] == higgsMass, "weight"] = 1000.0/len(self.df_test.loc[self.df_test["gen_higgs_mass"] == higgsMass])

    def scale_variables(self):
        # standard scaling
        if "standard_scaling" in self.config.keys() and self.config["standard_scaling"]:
            scaler = StandardScaler()
            numeric_columns = [i for i in self.config["training_features"] if "onehot" not in i and "jet" not in i] # Jets get their own scaler!
            if self.debug > 0:
                print("[PrepHelper] Standard Scaling the following numeric input features")
                print(numeric_columns)

            self.df_train[numeric_columns]  = scaler.fit_transform(self.df_train[numeric_columns])
            self.df_test[numeric_columns] = scaler.transform(self.df_test[numeric_columns])
            # jets
            if any(["jet" in training_feature for training_feature in self.config["training_features"]]):
                jet1Scaler = StandardScaler()
                jet1Columns = [i for i in self.config["training_features"] if "jet1" in i]
                jet2Scaler = StandardScaler()
                jet2Columns = [i for i in self.config["training_features"] if "jet2" in i]
                if self.debug > 0:
                    print("[PrepHelper] Adding separate scalers for jet variables!")
                    print(jet1Columns, jet2Columns)

                for columns, jetScaler in zip([jet1Columns, jet2Columns], [jet1Scaler, jet2Scaler]):
                    pt_variable = [string for string in columns if "pt" in string][0]

                    self.df_train.loc[self.df_train[pt_variable] > 0, columns] = jetScaler.fit_transform(self.df_train.loc[self.df_train[pt_variable] > 0, columns])
                    self.df_test.loc[self.df_test[pt_variable] > 0, columns] = jetScaler.transform(self.df_test.loc[self.df_test[pt_variable] > 0, columns])
                pkl.dump({"main":scaler, "jet1":jet1Scaler, "jet2":jet2Scaler},  open(self.output[:-5]+"_scaler_weights.pkl", "wb"))

            else: #legacy
                pkl.dump(scaler, open(self.output[:-5]+"_scaler_weights.pkl", "wb"))

        self.X_train = self.df_train[self.config["training_features"]]
        self.y_train = self.df_train[self.target]
        self.weight_train = self.df_train["weight"]

        self.X_test = self.df_test[self.config["training_features"]]
        self.y_test = self.df_test[self.target]
        self.weight_test = self.df_test["weight"]


        self.X_val = self.df_val[self.config["training_features"]]
        self.y_val = self.df_val[self.target]
        self.weight_val = self.df_val["weight"]

        self.n_train = len(self.df[self.df["train_label"] == 0])
        self.n_test = len(self.df[self.df["train_label"] == 1])
        self.n_validation = len(self.df[self.df["train_label"] == 2])

    def write_hdf5(self):
        self.X_train.to_hdf(self.output, "X_train")
        self.y_train.to_hdf(self.output, "y_train")
        self.weight_train.to_hdf(self.output, "weight_train")
        self.X_test.to_hdf(self.output, "X_test")
        self.y_test.to_hdf(self.output, "y_test")
        self.weight_test.to_hdf(self.output, "weight_test")

        df_output_name = self.input[:-4] + "_with_labels.pkl"
        self.df.to_pickle(df_output_name)
