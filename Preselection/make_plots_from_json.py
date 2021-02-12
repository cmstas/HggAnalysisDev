import pandas as pd
import numpy as np
from yahist import Hist1D, Hist2D
from utils import plot_stack
import mplhep
import awkward as ak
import numba as nb
from looper_utils import deltaR_devfunc
import sys
plt.style.use(mplhep.style.CMS)

class Plotter():
    """
    Plotter class - initialize an instance of this class, supply an input dataframe/hdf5/pickle, plot parameters json
    and get yield tables and plots out
    """
    def __init__(self,**kwargs):
        """
        input : dataframe or location of hdf5/pickle file
        input_options : json file or dict of the input dataframe if input is a pandas DF. Otherwise the json corresponding to pickle will be used
        samples : List of samples to be plotted
        options : json file containing the plot options. If not specified, then only table will be produced
        """
        self.input = kwargs.get("df")
        self.input_options = None
        self.plot_options = kwargs.get("plot_options")
        self.branches = kwargs.get("branches")
        self.debug = kwargs.get("debug")

        if kwargs.get("input_options"):
            self.input_options = kwargs.get("input_options")
        else:
            self.input_options = None

        if type(self.input) is str:
            #Open the file and store the dataframe in self.input
            if ".pkl" in self.input:
                self.input = pd.read_pickle(self.input)
                if not self.input_options:
                    self.input_options = self.input.replace(".pkl",".json")
            elif ".hdf" in self.input:
                self.input = pd.read_hdf(self.input)
                if not self.input_options:
                    self.input_options = self.input.replace(".hdf5",".json")
            else:
                print("Not a recognized format! Cannot Plot!")
                sys.exit(1)

            with open(self.input_options,"r") as f_in:
                self.input_options = json.load(f_in)

        elif type(self.input) is pd.DataFrame:
            if type(self.input_options) is str:
                with open(self.input_options,"r") as f_in:
                    self_input_options = json.load(f_in)
            else:
                print("No dataframe options json file or dict given! Cannot Plot!")
                sys.exit(1)
        else:
            print("Not a valid input! Cannot Plot!")
            sys.exit(1)
        #parse the plot options
        with open(self.plot_options,"r") as f_in:
            self.plot_options = json.load(f_in)
        #Samples specify which processes to plot. "all" implies everything will be plotted
        if self.debug > 0:
            print("[make_plots_from_json] Loaded dataframe and options")

    def run(self):
        self.preprocess()
        self.fill_hists()
#        self.make_tables()
        self.make_plots()
        return

    def preprocess():
        """ Splits the master dataframe into one for each process"""
        self.master_dataframe = {}
        self.process_id_map = {}
        for sample,info in self.input_options["samples_dict"].items():
            #FIXME: Hardcoded signal as HH_ggTauTau
            if sample == "HH_ggTauTau":
                self.process_id_map["signal"] = info["process_id"]
                self.master_dataframe["signal"] = self.input[self.input["process_id"] == info["process_id"]]
            else:
                self.process_id_map[sample] = info["process_id"]
                self.master_dataframe[sample] = self.input[self.input["process_id"] == info["process_id"]]

    def fill_hists(self):
        """Reads the json file for binning :-
        Then makes the histograms using YaHist and fills them
        """
        #TODO:Add cut processing here

        #self.plot_options holds the plot options
        self.histograms = {}
        for branch in self.branches:
            self.histograms[branch] = {} #one histogram per process
            for process in self.plot_options[branch]["processes"]:
                toFill = self.master_dataframe[process][branch]
                weights = self.master_dataframe[process]["weight"]
                #bin parsing
                if self.plot_options[branch]["bin_type"] = "linspace": #"list" or "linspace"
                    bins = np.linspace(self.plot_options[branch]["bins"][0],self.plot_options[branch]["bins"][1], self.plot_options[branch]["bins"][2]) #start, stop, nbins
                else:
                    bins = np.array(self.plot_options[branch][bins]) #custom binning
                self.histograms[branch][process] = Hist1D(toFill.values,bins = bins,weights = weights, label = self.plot_options[branch][label])


    def make_tables(self):
        """Composes a common table using the YaHists created"""
        #TODO:Splitting by year
        pass
    def make_plots(self):
        """Plots the YaHists properly (stacking the backgrounds, applying normalization, signals in solid line, data as points etc)"""
        for branch in self.branches:
            hist_stack = []
            for process,hist in self.histograms[branch].items():
                if process == "signal" or process == "Data":
                    continue
                else:
                    hist_stack.append(hist)
            sorted(hist_stack,key = lambda x : x.counts)
            fig,(ax1,ax2) = plt.subplots(2,sharex = True, figsize = (8,6), gridspec_kw = dict(height_ratios=[3,1]))
            plot_stack(hist_stack, ax = ax1)
            process[branch]["signal"].plot(histtype = "step", label = "signal", ax = ax1)
            process[branch]["data"].plot(show_errors = True, ax = ax1)
            total_background_counts = hist_stack[0].copy()
            for i in hist_stack[1:]:
                total_background_counts += i
            ratio_hist = process[branch]["data"].copy()
            ratio_hist /= total_background_counts
            ratio_hist.plot(ax = ax2, show_error = True, label = "ratio")
            plt.savefig("temp.pdf")


#unit test
if __name__ == "__main__":
    p = Plotter(df = "HggUnitTest.pkl",plot_options = "plot_options_test.json", branches = "ggMass",debug = True)
    p.run()
