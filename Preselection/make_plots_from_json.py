import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from yahist import Hist1D, Hist2D
from yahist.utils import plot_stack
import json
import mplhep as hep
import awkward as ak
import numba as nb
from looper_utils import deltaR_devfunc
import sys
plt.style.use([hep.style.CMS, hep.style.firamath])

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
                if not self.input_options:
                    self.input_options = self.input.replace(".pkl",".json")
                self.input = pd.read_pickle(self.input)
            elif ".hdf" in self.input:
                if not self.input_options:
                    self.input_options = self.input.replace(".hdf5",".json")
                self.input = pd.read_hdf(self.input)
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
        print(self.plot_options)
        #Samples specify which processes to plot. "all" implies everything will be plotted
        if self.debug > 0:
            print("[make_plots_from_json] Loaded dataframe and options")

    def run(self):
        self.preprocess()
        self.fill_hists()
#        self.make_tables()
        self.make_plots()
        return

    def preprocess(self):
        """ Splits the master dataframe into one for each process"""
        self.master_dataframe = {}
        self.process_id_map = {}
        for sample,info in self.input_options["samples_dict"].items():
            print("sample = ",sample)
            #FIXME: Hardcoded signal as HH_ggTauTau
            if sample == "HH_ggTauTau":
                self.process_id_map["signal"] = info["process_id"]
                self.master_dataframe["signal"] = self.input[self.input["process_id"] == info["process_id"]]
            elif "GJets" in sample:
                if "GJets" in self.process_id_map:
                    continue
                else:
                    self.process_id_map["GJets"] = info["process_id"]
                    self.master_dataframe["GJets"] = self.input[self.input["process_id"] == info["process_id"]]
 
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
                if self.plot_options[branch]["bin_type"] == "linspace": #"list" or "linspace"
                    bins = np.linspace(self.plot_options[branch]["bins"][0],self.plot_options[branch]["bins"][1], self.plot_options[branch]["bins"][2]) #start, stop, nbins
                else:
                    bins = np.array(self.plot_options[branch][bins]) #custom binning
                self.histograms[branch][process] = Hist1D(toFill.values,bins = bins,weights = weights, label = process)


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
            print([(k,v.integral) for k,v in self.histograms[branch].items()])
            hist_stack = sorted(hist_stack,key = lambda x : x.integral)
            fig,(ax1,ax2) = plt.subplots(2,sharex = True, gridspec_kw = dict(height_ratios=[3,1]))
            plot_stack(hist_stack, ax = ax1)
            if "yaxis" in self.plot_options[branch].keys():                 
                if self.plot_options[branch]["yaxis"] == "log":
                    ax1.set_yscale("log")
                else:
                    if self.debug:
                        print("Setting linear scale for y axis")
            else:
                print("No yaxis scale option given! Setting linear by default")
               
            if "signal_scaling" in self.plot_options[branch]:
                self.histograms[branch]["signal"] *= float(self.plot_options[branch]["signal_scaling"])
                signal_label = "signal x {}".format(self.plot_options[branch]["signal_scaling"])
            else:
                signal_label = "signal"
            self.histograms[branch]["signal"].plot(histtype = "step", label = signal_label, ax = ax1, color = "black")
            self.histograms[branch]["Data"].plot(show_errors = True, ax = ax1, color = "black")
            total_background_counts = hist_stack[0].copy()
            if "xlabel" in self.plot_options[branch].keys():
                ax1.set_xlabel(self.plot_options[branch]["xlabel"])
            else:
                ax1.set_xlabel(branch)
            if "ylim" in self.plot_options[branch].keys():
                ax1.set_ylim(self.plot_options[branch]["ylim"])
            ax1.legend(fontsize = 12)

            #Shamelessly stolen from mplhep
            if ax1.get_yscale() == "log":
                scale_factor = 11.2
            else:
                scale_factor = 1.0
            print("axes limits = ",ax1.get_ylim())
            while hep.plot.overlap(ax1,hep.plot._draw_leg_bbox(ax1)) > 0:
                ax1.set_ylim(ax1.get_ylim()[0],ax1.get_ylim()[-1] * scale_factor)
                ax1.figure.canvas.draw()


            if "cms_label" in self.plot_options[branch] and self.plot_options[branch]["cms_label"]:
                plt.sca(ax1)
                hep.cms.label(loc = 0, data = True, lumi = 137.2,fontsize = 18)         
                plt.sca(ax2)
            for i in hist_stack[1:]:
                total_background_counts += i.copy()
            ratio_hist = self.histograms[branch]["Data"].copy()
            ratio_hist /= total_background_counts
            ax2.set_yscale("log")
            if "ratio_ylim" in self.plot_options[branch].keys():
                ax2.set_ylim(self.plot_options[branch]["ratio_ylim"])
            ratio_hist.plot(ax = ax2, show_errors = True, label = "ratio")
            #Title
            if "title" in self.plot_options[branch].keys():
                ax1.set_title(self.plot_options[branch]["title"],fontsize = 18)
            else:
                ax1.set_title(branch,fontsize = 18)
            plt.savefig("temp.pdf")


#unit test
if __name__ == "__main__":
    p = Plotter(df = "HggUnitTest.pkl",plot_options = "plot_options_test.json", branches = ["ggMass"],debug = True)
    p.run()
