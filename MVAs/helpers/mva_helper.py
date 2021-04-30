import h5py
import pandas
import json
import numpy
import matplotlib.pyplot as plt

from . import utils
from . import bdt_helper

class MVAHelper():
    """
    Class to read events in from an ntuple and perform necessary
    preprocessing, sample labeling, etc and then write them
    to an output hdf5 file to be used for BDT/DNN trainig
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.config_file = kwargs.get("config")
        self.output_tag = kwargs.get("output_tag")
        self.debug = kwargs.get("debug")

        with open(self.config_file, "r") as f_in:
            self.config = json.load(f_in)

        if self.debug > 0:
            print("[MVAHelper] Creating MVAHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

    def run(self):
        self.load_events()
        self.train()
        self.predict()
        self.evaluate_performance()
        self.save_weights()

    def evaluate(self, weight_file):
        self.load_events()
        self.load_weights(weight_file)
        self.predict()
        self.evaluate_performance()

    def load_events(self):
        self.events = {}
        for split in ["train", "test"]:
            self.events[split] = {}
            for data in ["X", "y", "weight"]:
                self.events[split][data] = pandas.read_hdf(self.input, "%s_%s" % (data, split))
            for label, val in zip(["signal", "background"], [1, 0]):
                self.events[split]["n_%s_raw" % label] = len(self.events[split]["y"].loc[self.events[split]["y"] == val])
                self.events[split]["n_%s_weighted" % label] = (self.events[split]["weight"][self.events[split]["y"] == val]).sum()

                if self.debug > 0:
                    print("[MVAHelper] For set: %s and label: %s, loaded %.6f (%d) weighted (raw) events" % (split, label, self.events[split]["n_%s_weighted" % label], self.events[split]["n_%s_raw" % label]))

        return

    def initialize_train_helper(self):
        if self.config["mva"]["type"] == "binary_classification_bdt":
            self.train_helper = bdt_helper.BDTHelper(
                events = self.events,
                config = self.config,
                output_tag = self.output_tag,
                debug = self.debug
            )
        return

    def load_weights(self, weight_file):
        self.initialize_train_helper()
        self.mva = self.train_helper.load_weights(weight_file)
        return

    def train(self):
        self.initialize_train_helper()
        self.mva = self.train_helper.train()
        return

    def predict(self):
        self.prediction = self.train_helper.predict()

        return

    def evaluate_performance(self):
        self.performance = {}
        for split in self.events.keys():
            self.performance[split] = utils.calc_roc_and_unc(
                self.events[split]["y"],
                self.prediction[split],
                self.events[split]["weight"],
                n_bootstrap = 25
            )

            if self.debug > 0:
                print("[MVA_HELPER] Performance (%s set): AUC = %.3f +/- %.3f" % (split, self.performance[split]["auc"], self.performance[split]["auc_unc"]))
        
        self.make_plots()
        self.save_performance()

    def make_plots(self):
        self.plots = []
        for split in self.events.keys():
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            ax1.yaxis.set_ticks_position('both')
            ax1.grid(True)

            ax1.plot(self.performance[split]["fpr"],
                     self.performance[split]["tpr"],
                     color = "red",
                     label = "BDT AUC: %.3f +/- %.3f" % (self.performance[split]["auc"], self.performance[split]["auc_unc"]))
            ax1.fill_between(self.performance[split]["fpr"],
                             self.performance[split]["tpr"] - (self.performance[split]["tpr_unc"]/2.),
                             self.performance[split]["tpr"] + (self.performance[split]["tpr_unc"]/2.),
                             color = "red",
                             alpha = 0.25, label = r'$\pm 1\sigma')

            plt.xlim([-0.05,1.05])
            plt.ylim([-0.05,1.05])
            plt.xlabel("False Positive Rate")
            plt.ylabel("True Positive Rate")
            plt.legend(loc = "lower right")
            plot_name = "output/roc_comparison_%s_%s.pdf" % (self.output_tag, split)
            plt.savefig(plot_name)
            self.plots.append(plot_name)
            plt.clf()

    def save_performance(self):
        """
        Save roc curves to npz file
        """
        self.npz_file = "output/" + self.output_tag + ".npz"
        self.npz_results = {}
        for split in self.events.keys():
            for metric in self.performance[split].keys():
                self.npz_results[metric + "_" + split] = self.performance[split][metric]
            for info in ["weight", "y"]:
                self.npz_results[info + "_" + split] = self.events[split][info]
        numpy.savez(self.npz_file, **self.npz_results)        
        return

    def save_weights(self):
        self.summary = self.train_helper.save_weights()
        self.summary["plots"] = self.plots 
        self.summary["npz_file"] = self.npz_file

        self.summary_file = "output/" + self.output_tag + ".json"
        with open(self.summary_file, "w") as f_out:
            json.dump(self.summary, f_out, sort_keys = True, indent = 4)

        return
