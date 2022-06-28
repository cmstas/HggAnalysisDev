import h5py
import pandas
import json
import numpy as np
import random
import awkward as ak
import matplotlib.pyplot as plt
import xgboost

from . import utils
from . import bdt_helper

class PrepHelper():
    """
    Class to read events in from an ntuple and perform necessary
    preprocessing, sample labeling, etc and then write them
    to an output hdf5 file to be used for BDT/DNN training
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.output = kwargs.get("output")
        self.output_tag = self.output.replace('.hdf5', '').replace('output/','')
        self.debug = kwargs.get("debug")
        self.config_file = kwargs.get("config")

        if self.debug > 0:
            print("[PrepHelper] Creating PrepHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        with open(self.input.replace("merged_nominal.parquet", "summary.json"), "r") as f_in:
            print(f_in)
            self.input_config = json.load(f_in)
        self.make_process_id_map()

        with open(self.config_file, "r") as f_in:
            self.config = json.load(f_in)

        self.df = ak.from_parquet(self.input)
        if self.debug > 0:
            print("[PrepHelper] Loaded file %s, containing %d events" % (self.input, len(self.df)))

    def run(self):
        self.prepare_samples()
        self.preprocess() # scale sig/bkg yields, preprocess individual features, etc
        self.prepare_features()
        self.make_train_test_validation_split()
        #self.write_hdf5()
        self.train()
        self.predict()
        self.evaluate_performance()
        self.save_weights()
        
        return

    def make_process_id_map(self):
        self.process_id_map = {}
        for sample, info in self.input_config["sample_id_map"].items():
            self.process_id_map[sample] = info

        if self.debug > 0:
            print("[PrepHelper] process_id map: ", self.process_id_map)
        return

    def preprocess(self):
        if self.config["preprocess"]["scale_signal"]: # scale signal yield to bkg yield
            #self.df.loc[self.df["label"] == 1, "weight_central"] *= self.n_background_weighted / self.n_signal_weighted
            scale = self.n_background_weighted / self.n_signal_weighted
            self.df['weight_central'] = ak.where(
                self.df.label == 1,
                self.df.weight_central * scale,
                self.df.weight_central
            )
            self.n_signal_reweighted = np.sum(self.df["weight_central"][self.df["label"] == 1])

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

        self.df['label'] = ak.ones_like(self.df.weight_central) * -1
        for proc in self.process_id_map:
            if proc == 'Data':
                label = -1
            elif proc in self.config['signal']:
                label = 1
            elif proc in self.config['background']:
                label = 0
            else:
                continue
            self.df['label'] = ak.where(
                self.df.process_id == self.process_id_map[proc],
                label,
                self.df.label
            )

        #self.df = self.df[self.df["process_id"].isin(self.process_ids)]
        m_sig = self.df.label==1
        b_sig = self.df.label==0
        self.df = self.df[m_sig|b_sig]
        if self.debug > 0:
            print("[PrepHelper] After selecting for signals and backgrounds, dataframe contains %d events" % (len(self.df)))

#        label = list(np.zeros(len(self.df)))
#
#        self.df["label"] = label
#        self.df = self.df.reset_index(drop = True) # reassign indices so we can do test/train/val splits more easily later
#
#        # Assign signal events label of 1
#        for process in self.config["signal"]:
#            self.df.loc[self.df["process_id"] == self.process_id_map[process], "label"] = 1

        self.n_signal = len(self.df[self.df["label"] == 1])
        self.n_signal_weighted = np.sum(self.df["weight_central"][self.df["label"] == 1])

        self.n_background = len(self.df[self.df["label"] == 0])
        self.n_background_weighted = np.sum(self.df["weight_central"][self.df["label"] == 0])

        if self.debug > 0:
            print("[PrepHelper] After labeling, have %d signal events (%.6f weighted) and %d background events (%.6f weighted)" % (self.n_signal, self.n_signal_weighted, self.n_background, self.n_background_weighted))

        return

    def prepare_features(self):
        self.X = self.df[self.config["training_features"]]
        self.y = self.df.label
        self.weight = self.df["weight_central"]

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

        self.X_train = ak.to_numpy(ak.values_astype(self.X[idx_train], np.float64))
        self.X_train = self.X_train.view((float, len(self.X_train.dtype.names)))
        self.y_train = self.y[idx_train]
        self.weight_train = self.weight[idx_train]
        self.X_test = ak.to_numpy(ak.values_astype(self.X[idx_test], np.float64))
        self.X_test = self.X_test.view((float, len(self.X_test.dtype.names)))
        self.y_test = self.y[idx_test]
        self.weight_test = self.weight[idx_test]
        self.X_validation = self.X[idx_validation]
        self.y_validation = self.y[idx_validation]
        self.weight_validation = self.weight[idx_validation]

        self.events = {}
        self.events['train'] = {}
        self.events['test'] = {}
        self.events['train']['X'] = self.X_train
        self.events['train']['y'] = self.y_train
        self.events['train']['weight'] = self.weight_train
        self.events['test']['X'] = self.X_test
        self.events['test']['y'] = self.y_test
        self.events['test']['weight'] = self.weight_test

        for split in ['train', 'test']:
            for label, val in zip(['signal', 'background'], [1,0]):
                self.events[split]['n_%s_raw' % label] = ak.count_nonzero(self.events[split]['y'] == val)
                self.events[split]['n_%s_weighted' % label] = ak.sum(self.events[split]['weight'][self.events[split]['y'] == val])

                if self.debug > 0:
                    print("[MVAHelper] For set: %s and label: %s, loaded %.6f (%d) weighted (raw) events" % (split, label, self.events[split]["n_%s_weighted" % label], self.events[split]["n_%s_raw" % label]))

#        self.df.iloc[idx_train, self.df.columns.get_loc("train_label")] = 0
#        self.df.iloc[idx_test, self.df.columns.get_loc("train_label")] = 1
#        self.df.iloc[idx_validation, self.df.columns.get_loc("train_label")] = 2

        self.n_train = len(self.df[self.df["train_label"] == 0])
        self.n_test = len(self.df[self.df["train_label"] == 1])
        self.n_validation = len(self.df[self.df["train_label"] == 2])

        if self.debug > 0:
            print("[PrepHelper] Have %d/%d/%d events in train/test/validation splits" % (self.n_train, self.n_test, self.n_validation))

        return

    def write_hdf5(self):
        fout = h5py.File(self.output, 'w')
        X_train = fout.create_group('X_train')
        y_train = fout.create_group('y_train')
        weight_train = fout.create_group('weight_train')
        X_test = fout.create_group('X_test')
        y_test = fout.create_group('y_test')
        weight_test = fout.create_group('weight_test')

        xrform, xrlength, xrcontainer = ak.to_buffers(ak.packed(self.X_train), container=X_train)
        yrform, yrlength, yrcontainer = ak.to_buffers(ak.packed(self.y_train), container=y_train)
        wrform, wrlength, wrcontainer = ak.to_buffers(ak.packed(self.weight_train), container=weight_train)
        xeform, xelength, xecontainer = ak.to_buffers(ak.packed(self.X_test), container=X_test)
        yeform, yelength, yecontainer = ak.to_buffers(ak.packed(self.y_test), container=y_test)
        weform, welength, wecontainer = ak.to_buffers(ak.packed(self.weight_test), container=weight_test)

        fout.close()

        #self.X_train.to_hdf(self.output, "X_train")
        #self.y_train.to_hdf(self.output, "y_train")
        #self.weight_train.to_hdf(self.output, "weight_train")
        #self.X_test.to_hdf(self.output, "X_test")
        #self.y_test.to_hdf(self.output, "y_test")
        #self.weight_test.to_hdf(self.output, "weight_test")

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

    def train(self):
        self.initialize_train_helper()
        self.mva = self.train_helper.train()
        return()

    def predict(self):
        self.prediction = self.train_helper.predict()
        print(self.prediction)
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
        np.savez(self.npz_file, **self.npz_results)        
        return

    def save_weights(self):
        self.summary = self.train_helper.save_weights()
        self.summary["plots"] = self.plots 
        self.summary["npz_file"] = self.npz_file

        self.summary_file = "output/" + self.output_tag + ".json"
        with open(self.summary_file, "w") as f_out:
            json.dump(self.summary, f_out, sort_keys = True, indent = 4)

        return



