import h5py
import pandas
import json
import xgboost

from . import utils

class BDTHelper():
    """
    Class to read events in from an ntuple and perform necessary
    preprocessing, sample labeling, etc and then write them
    to an output hdf5 file to be used for BDT/DNN trainig
    """

    def __init__(self, **kwargs):
        self.events = kwargs.get("events")
        self.config = kwargs.get("config")
        self.output_tag = kwargs.get("output_tag", "")
        self.debug = kwargs.get("debug")
        self.made_dmatrix = False

    def train(self):
        self.make_dmatrix()
        if self.config["mva"]["type"] == "binary_classification_bdt":
            eval_list = [(self.events["train"]["dmatrix"], "train"), (self.events["test"]["dmatrix"], "test")]
            progress = {}

            if self.debug > 0:
                print("[BDTHelper] Training BDT with options:")
                print(self.config["mva"]["param"])

            if self.config["mva"]["early_stopping"]:
                n_early_stopping =  self.config["mva"]["early_stopping_rounds"]
                print("[BDTHelper] early stopping with %d rounds (%d maximum)" % (n_early_stopping, self.config["mva"]["n_trees"]))
            else:
                print("[BDTHelper] using %d trees (no early stopping)" % (self.config["mva"]["n_trees"]))
                n_early_stopping = None

            self.bdt = xgboost.train(
                self.config["mva"]["param"],
                self.events["train"]["dmatrix"],
                self.config["mva"]["n_trees"],
                eval_list, evals_result = progress,
                early_stopping_rounds = n_early_stopping
            )

        # TODO : multiclass BDT
        return self.bdt

    def make_dmatrix(self):
        for split in self.events.keys():
            self.events[split]["dmatrix"] = xgboost.DMatrix(
                self.events[split]["X"],
                self.events[split]["y"],
                weight = abs(self.events[split]["weight"])
            )
        self.made_dmatrix = True
        return

    def predict_from_df(self, df):
        X = xgboost.DMatrix(df[self.config["training_features"]])
        return self.bdt.predict(X)

    def predict(self):
        if not self.made_dmatrix:
            self.make_dmatrix()
        self.prediction = {}
        for split in self.events.keys():
            self.prediction[split] = self.bdt.predict(self.events[split]["dmatrix"])
        return self.prediction

    def save_weights(self):
        self.weights_file =  "output/" + self.output_tag + ".xgb"
        self.summary_file = self.weights_file.replace(".xgb", ".json")
        self.bdt.save_model(self.weights_file)
        summary = {
            "config" : self.config,
            "weights" : self.weights_file
        }
        with open(self.summary_file, "w") as f_out:
            json.dump(summary, f_out, sort_keys = True, indent = 4)

        return summary

    def load_weights(self, weight_file):
        self.bdt = xgboost.Booster()
        self.bdt.load_model(weight_file)

