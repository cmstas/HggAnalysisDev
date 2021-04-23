import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from yahist import Hist1D
from yahist.utils import plot_stack
import json
import mplhep as hep
import sys

plt.style.use([hep.style.CMS, hep.style.firamath])


class Plotter:
    """
    Plotter class - initialize an instance of this class,
    supply an input dataframe/hdf5/pickle, plot parameters json
    and get yield tables and plots out
    """

    def __init__(self, **kwargs):
        """
        df : dataframe or location of hdf5/pickle file

        input_options : json file or a dictionary of the input dataframe
        if input is a pandas DF. Otherwise the json corresponding to pickle
        will be used

        branches : List of branches to be plotted (string if single branch). If
        "all" specified, then all the branches from the plot_options json file
        will be plotted

        plot_options : json file or dictionary containing the plot options.
        If not specified, then only table will be produced

        debug : bool specifies if debug messages need to be printed

        save_filenames : List of filenames to be used for saving the plots. If
        "all" branches specified or the lengths of this list and the branches
        list don't match, then the names from the plot_options json
        will be used.
        """

        self.input = kwargs.get("df")
        self.input_options = None
        self.plot_options = kwargs.get("plot_options")
        self.branches = kwargs.get("branches")

        if kwargs.get("debug"):
            self.debug = kwargs.get("debug")
        else:
            self.debug = False

        if kwargs.get("save_filenames"):
            self.save_filenames = kwargs.get("save_filenames")
        else:
            self.save_filenames = None

        if type(self.branches) == str:
            self.branches = [self.branches]

        if type(self.save_filenames) == str:
            self.save_filenames = [self.save_filenames]

        if self.save_filenames and self.branches[0] == "all":
            print(
                "[plotter.py] Plot names will be read from the json file if \
                requesting to plot all branches"
            )
            self.save_filenames = None

        elif self.save_filenames and len(self.branches) != len(
            self.save_filenames
        ):
            print(
                "[plotter.py] Number of save file names do not match the \
                        number of branches! Using default names from json"
            )
            self.save_filenames = None

        if kwargs.get("input_options"):
            self.input_options = kwargs.get("input_options")
        else:
            self.input_options = None

        if type(self.input) is str:
            # Open the file and store the dataframe in self.input
            if ".pkl" in self.input:
                if not self.input_options:
                    self.input_options = self.input.replace(".pkl", ".json")
                self.input = pd.read_pickle(self.input)
            elif ".hdf" in self.input:
                if not self.input_options:
                    self.input_options = self.input.replace(".hdf5", ".json")
                self.input = pd.read_hdf(self.input)
            else:
                print("Not a recognized format! Cannot Plot!")
                sys.exit(1)

            with open(self.input_options, "r") as f_in:
                self.input_options = json.load(f_in)

        elif type(self.input) is pd.DataFrame:
            if type(self.input_options) is str:
                with open(self.input_options, "r") as f_in:
                    self.input_options = json.load(f_in)
            elif type(self.input_options) is dict:
                pass  # do nothing
            else:
                print(
                    "No dataframe options json file or dict given! Cannot Plot\
                            !"
                )
                sys.exit(1)
        else:
            print("Not a valid input! Cannot Plot!")
            sys.exit(1)
        # parse the plot options
        if type(self.plot_options) is str:
            with open(self.plot_options, "r") as f_in:
                self.plot_options = json.load(f_in)
        elif type(self.plot_options) is dict:
            pass  # do nothing
        else:
            print(
                "plot_options not properly provided! Provide json file or dict"
            )
        if self.debug:
            print("[plotter.py] Loaded dataframe and options")

    def run(self):
        self.preprocess()
        self.fill_hists()
        self.make_plots()
        return

    def preprocess(self):
        """ Splits the master dataframe into one for each process"""
        self.master_dataframe = {}
        self.process_id_map = {}
        for sample, info in self.input_options["samples_dict"].items():
            if self.debug:
                print("[plotter.py] sample = ", sample)
            # FIXME: Hardcoded signal as HH_ggTauTau
            if sample == "HH_ggTauTau":
                self.process_id_map["signal"] = info["process_id"]
                self.master_dataframe["signal"] = self.input[
                    self.input["process_id"] == info["process_id"]
                ]
            elif "GJets" in sample:
                if "GJets" in self.process_id_map:
                    continue
                else:
                    self.process_id_map["GJets"] = info["process_id"]
                    self.master_dataframe["GJets"] = self.input[
                        self.input["process_id"] == info["process_id"]
                    ]

            else:
                self.process_id_map[sample] = info["process_id"]
                self.master_dataframe[sample] = self.input[
                    self.input["process_id"] == info["process_id"]
                ]

    def fill_hists(self):
        """Reads the json file for binning :-
        Then makes the histograms using YaHist and fills them
        """
        # TODO:Add cut processing here

        # self.plot_options holds the plot options
        self.histograms = {}
        if self.branches == ["all"]:
            self.branches = list(self.plot_options.keys())
        for idx, branch in enumerate(self.branches):
            self.histograms[branch] = {}  # one histogram per process
            for process in self.plot_options[branch]["processes"]:
                if branch not in self.master_dataframe[process].columns:
                    print(
                        "[plotter.py] {} not found in the dataframe. Skipping..\
                                .".format(
                            branch
                        )
                    )
                    del self.histograms[branch]
                    del self.branches[idx]
                    break
                toFill = self.master_dataframe[process][branch]
                weights = self.master_dataframe[process]["weight"]
                # bin parsing
                if (
                    self.plot_options[branch]["bin_type"] == "linspace"
                ):  # "list" or "linspace"
                    bins = np.linspace(
                        self.plot_options[branch]["bins"][0],
                        self.plot_options[branch]["bins"][1],
                        self.plot_options[branch]["bins"][2],
                    )  # start, stop, nbins
                else:
                    bins = np.array(
                        self.plot_options[branch]["bins"]
                    )  # custom binning
                self.histograms[branch][process] = Hist1D(
                    toFill.values, bins=bins, weights=weights, label=process
                )

    def make_tables(self):
        """Composes a common table using the YaHists created"""
        # Create the histograms if required
        if len(self.histograms) == 0:
            self.preprocess()
            self.fill_hists()

        mdf = open("tables.md", "w")
        for branch in self.branches:
            representative_key = list(self.histograms[branch].keys())[0]
            bin_lefts = self.histograms[branch][representative_key].edges[:-1]
            bin_rights = self.histograms[branch][representative_key].edges[1:]
            mdf.write("| {} ".format(branch))
            for bin_number in range(len(bin_lefts)):
                mdf.write(
                    "| {:0.2f} - {:0.2f} ".format(
                        bin_lefts[bin_number], bin_rights[bin_number]
                    )
                )
            mdf.write("|\n")

            mdf.write("| --- ")
            for bin_number in range(len(bin_lefts)):
                mdf.write("| --- ")
            mdf.write("| --- |\n")
            for process in self.histograms[branch].keys():
                mdf.write("| {} ".format(process))
                for bin_number in range(len(bin_lefts)):
                    mdf.write(
                        "| {:0.2f} $\\pm$ {:0.2f} ".format(
                            self.histograms[branch][process].counts[
                                bin_number
                            ],
                            self.histograms[branch][process].errors[
                                bin_number
                            ],
                        )
                    )
                mdf.write("|\n")
            mdf.write("\n\n")
        mdf.close()

    def make_plots(self):
        """Plots the YaHists properly (stacking the backgrounds, applying
        normalization, signals in solid line, data as points etc)"""

        for idx, branch in enumerate(self.branches):
            print("Making plots for branch ", branch)
            if "Data" in self.histograms[branch]:
                fig, (ax1, ax2) = plt.subplots(
                    2, sharex=True, gridspec_kw=dict(height_ratios=[3, 1])
                )
            else:
                fig, ax1 = plt.subplots()

            hist_stack = []
            for process, hist in self.histograms[branch].items():
                if process == "signal" or process == "Data":
                    continue
                else:
                    hist_stack.append(hist)

            # stack plotting

            # Extra fancy feature - normalize and plot stack!
            if (
                "normalize" in self.plot_options[branch].keys()
                and self.plot_options[branch]["normalize"] == "unit_area"
            ):
                unit_normalize = True
            else:
                unit_normalize = False

            if (
                "stack" in self.plot_options[branch].keys()
                and self.plot_options[branch]["stack"] == 0
            ):
                stack = False

            else:
                stack = True

            if stack:
                hist_stack = sorted(hist_stack, key=lambda x: x.integral)
                total_sum = sum([x.integral for x in hist_stack])
                if unit_normalize:  # Special case - normalize stack!
                    for i in range(len(hist_stack)):
                        hist_stack[i] /= total_sum
                plot_stack(hist_stack, ax=ax1, histtype="stepfilled")
            else:
                if self.debug:
                    print("[plotter.py] No stacking for branch ", branch)
                for hist in hist_stack:
                    if unit_normalize:
                        hist /= hist.integral
                    hist.plot(ax=ax1, histtype="stepfilled")

            if "yaxis" in self.plot_options[branch].keys():
                if self.plot_options[branch]["yaxis"] == "log":
                    ax1.set_yscale("log")
                else:
                    if self.debug:
                        print("[plotter.py] Setting linear scale for y axis")
            else:
                print("No yaxis scale option given! Setting linear by default")

            # Plotting signal
            if "signal" in self.histograms[branch]:
                if (
                    not unit_normalize
                    and "signal_scaling" in self.plot_options[branch]
                ):
                    self.histograms[branch]["signal"] *= float(
                        self.plot_options[branch]["signal_scaling"]
                    )
                    signal_label = "signal x {:0.3f}".format(
                        self.plot_options[branch]["signal_scaling"]
                    )
                else:
                    signal_label = "signal"

                if unit_normalize:
                    self.histograms[branch]["signal"] /= self.histograms[
                        branch
                    ]["signal"].integral
                self.histograms[branch]["signal"].plot(
                    histtype="step", label=signal_label, ax=ax1, color="black"
                )

            if "xlabel" in self.plot_options[branch].keys():
                ax1.set_xlabel(self.plot_options[branch]["xlabel"])
            elif "title" in self.plot_options[branch].keys():
                ax1.set_xlabel(self.plot_options[branch]["title"])
            else:
                ax1.set_xlabel(branch)
            if "ylim" in self.plot_options[branch].keys():
                ax1.set_ylim(self.plot_options[branch]["ylim"])
            ax1.legend(fontsize=10)

            if (
                "cms_label" in self.plot_options[branch]
                and self.plot_options[branch]["cms_label"]
            ):
                plt.sca(ax1)
                hep.cms.label(loc=0, data=True, lumi=137.2, fontsize=18)

            # Plotting Data

            if "Data" in self.histograms[branch]:
                self.histograms[branch]["Data"].plot(
                    show_errors=True, ax=ax1, color="black"
                )
                total_background_counts = hist_stack[0].copy()

                for i in hist_stack[1:]:
                    total_background_counts += i.copy()
                ratio_hist = self.histograms[branch]["Data"].copy()
                ratio_hist /= total_background_counts
                plt.sca(ax2)
                if "ratio_log" in self.plot_options[branch].keys():
                    if self.plot_options[branch]["ratio_log"]:
                        ax2.set_yscale("log")

                if "ratio_ylim" in self.plot_options[branch].keys():
                    ax2.set_ylim(self.plot_options[branch]["ratio_ylim"])

                ratio_hist.plot(ax=ax2, show_errors=True, label="ratio")
                ax1.legend(fontsize=10)

                # Shamelessly stolen from mplhep
                if self.debug:
                    print(
                        "[plotter.py] Rescaling y axis to accommodate legend"
                    )
                if ax1.get_yscale() == "log":
                    scale_factor = 11.2
                else:
                    scale_factor = 1.05
                while hep.plot.overlap(ax1, hep.plot._draw_leg_bbox(ax1)) > 0:
                    ax1.set_ylim(
                        ax1.get_ylim()[0], ax1.get_ylim()[-1] * scale_factor
                    )
                    ax1.figure.canvas.draw()

            # Title
            if "title" in self.plot_options[branch].keys():
                ax1.set_title(self.plot_options[branch]["title"], fontsize=18)
            else:
                ax1.set_title(branch, fontsize=18)

            if self.save_filenames:
                plt.savefig(self.save_filenames[idx])
            elif "output_name" in self.plot_options[branch].keys():
                plt.savefig(self.plot_options[branch]["output_name"])
                if self.debug:
                    print(
                        "[plotter.py] Saved plot at {}".format(
                            self.plot_options[branch]["output_name"]
                        )
                    )
            else:
                plt.savefig("plot_{}.pdf".format(branch))
                if self.debug:
                    print(
                        "[plotter.py] Saved plot at {}".format(
                            "plot_{}.pdf".format(branch)
                        )
                    )


# unit test
if __name__ == "__main__":
    p = Plotter(
        df="HggUnitTest.pkl",
        plot_options="plot_options_test.json",
        branches="all",
        debug=True,
        save_filenames=["abc", "bcd", "cda"],
    )
    p.run()

    table_test = Plotter(
        df="HggUnitTest.pkl",
        plot_options="plot_options_test.json",
        branches=["ele1_eta"],
        debug=True,
    )
    table_test.run()
    table_test.make_tables()
