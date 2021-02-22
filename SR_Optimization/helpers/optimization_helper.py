import pandas
import json
import itertools

from helpers import utils, model_helper

class OptimizationHelper():
    """
    Class to take an input ntuple with MVA scores and optimize cuts
    on MVA scores in order to maximize expected sensitivity for some
    metric (significance, upper limit, etc)
    """

    def __init__(self, **kwargs):
        self.input = kwargs.get("input")
        self.debug = kwargs.get("debug")
        self.output_dir = kwargs.get("output_dir")
        self.output_tag = kwargs.get("output_tag")
        self.optimization_options = kwargs.get("optimization_options")
        with open(self.optimization_options, "r") as f_in:
            self.options = json.load(f_in)

        self.samples_file = kwargs.get("samples")
        with open(self.samples_file, "r") as f_in:
            self.samples = json.load(f_in)

        self.metric = kwargs.get("metric")

        self.batch = kwargs.get("batch")
        self.nCores = kwargs.get("nCores")

        if self.debug > 0:
            print("[OptimizationHelper] Creating OptimizationHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        self.results = {}

    def run(self):
        # 1. Calculate quantiles -> mva score
        # 2. For self.options["n_points"] evenly spaced cuts in signal eff:
        #   2.1 Get events passing cut
        #   2.2 Build signal model
        #   2.3 Build background model
        #   2.4 Fit m_gg spectrum, extract desired quantity

        self.load_events()    
        self.calculate_mva_cuts()
        self.scan_cuts()

        return

    def load_events(self):
        """
        Load pandas dataframe from input file.
        Trim df to have only validation events of the selected signal/background processes,
        as well as data.
        Also trim uneeded columns.
        """

        self.make_process_id_map()
        
        events = pandas.read_pickle(self.input)

        if self.debug > 0:
            print("[OptimizationHelper] Loaded dataframe from file %s with %d events" % (self.input, len(events)))

        columns = self.options["mvas"] + self.options["branches"]
        events = events[columns] # drop unneeded columns

        self.signal_ids = []
        for process in self.options["signal"]:
            self.signal_ids.append(self.process_id_map[process]) 

        self.resonant_background_ids = []
        for process in self.options["resonant_background"]:
            self.resonant_background_ids.append(self.process_id_map[process])

        self.background_ids = []
        for process in self.options["background"]:
            self.background_ids.append(self.process_id_map[process])

        self.signal_events = events[events["process_id"].isin(self.signal_ids)] 
        self.resonant_background_events = events[events["process_id"].isin(self.resonant_background_ids)]
        self.background_events = events[events["process_id"].isin(self.background_ids)]
        self.data_events = events[events["process_id"].isin([0])] # data should always be process_id = 0

        if self.debug > 0:
            print("[OptimizationHelper] Trimmed dataframes of signal/resonant background/background/data events have %.6f/%.6f/%.6f/%.6f (%d/%d/%d/%d) weighted (raw) events" % (self.signal_events["weight"].sum(), self.resonant_background_events["weight"].sum(), self.background_events["weight"].sum(), self.data_events["weight"].sum(), len(self.signal_events), len(self.resonant_background_events), len(self.background_events), len(self.data_events)))


        # Keep only validation events
        self.signal_events = self.signal_events[self.signal_events["train_label"] == 2]
        self.resonant_background_events = self.resonant_background_events[self.resonant_background_events["train_label"] == 2]
        self.background_events = self.background_events[self.background_events["train_label"] == 2]

        # NOTE: this assumes we always have an equal test/train/validation split.
        self.signal_events["weight"] *= 3
        self.resonant_background_events["weight"] *= 3
        self.background_events["weight"] *= 3

        if self.debug > 0:
            print("[OptimizationHelper] After keeping only validation events, have %.6f/%.6f/%.6f (%d/%d/%d) weighted (raw) signal/resonant background/background events" % (self.signal_events["weight"].sum(), self.resonant_background_events["weight"].sum(), self.background_events["weight"].sum(), len(self.signal_events), len(self.resonant_background_events), len(self.background_events)))

        return

    def calculate_mva_cuts(self):
        """
        For each mva listed in self.options["mvas"], calculate self.options["n_points"] evenly
        spaced cuts in signal efficiency.
        Will be calculated as the efficiency on all samples listed under self.options["signal"]
        """

        self.cut_values = {}
        self.cut_combos = {}
        for mva in self.options["mvas"]:
            self.cut_values[mva] = utils.calculate_cut_values(
                self.options["n_points"],
                self.signal_events[mva]
            )
        
            if self.debug > 1:
                print("[OptimizationHelper] For MVA %s with %d evenly spaced (in signal eff. cuts), the cut values are: " % (mva, self.options["n_points"]))
                print(self.cut_values[mva])

            self.cut_combos[mva] = list(itertools.combinations(
                range(self.options["n_points"]),
                self.options["n_bins"]
            ))

            if self.debug > 0:
                print("[OptimizationHelper] For MVA %s, scanning %d total cut combinations" % (mva, len(self.cut_combos[mva])))
            if self.debug > 1:
                print("[OptimizationHelper] For MVA %s, these cut combos are: " % (mva))
                print(self.cut_combos[mva])

        return

    def scan_cuts(self):
        """
         
        """
        #TODO implement for N-d optimization. Currently only supporting 1-d optimization (cut on 1 MVA)
        mva = self.options["mvas"][0] 
        idx = 0 # for logging results
        for cut_combo in self.cut_combos[mva]:
            idx += 1
            signal_events = []
            resonant_background_events = []
            background_events = []
            data_events = []
            for i in range(self.options["n_bins"]):
                # We assume cuts will be in ascending order, i.e. cut_combo[0] < cut_combo[1] < ...
                cut_lower = self.cut_values[mva][cut_combo[i]]
                cut_upper = 10e9 if (i == self.options["n_bins"] - 1) else self.cut_values[mva][cut_combo[i+1]]

                signal_events_bin = self.signal_events.loc[self.signal_events[mva].between(cut_lower, cut_upper, inclusive=True)]
                resonant_background_events_bin = self.resonant_background_events.loc[self.resonant_background_events[mva].between(cut_lower, cut_upper, inclusive=True)]
                background_events_bin = self.background_events.loc[self.background_events[mva].between(cut_lower, cut_upper, inclusive=True)]
                data_events_bin = self.data_events.loc[self.data_events[mva].between(cut_lower, cut_upper, inclusive=True)]

                if self.debug > 1:
                    print("[OptimizationHelper] For MVA %s, cutting on mva score between %.6f and %.6f yields %.6f/%.6f/%.6f/%.6f events in signal/resonant background/background/data" % (mva, cut_lower, cut_upper, signal_events_bin["weight"].sum(), resonant_background_events_bin["weight"].sum(), background_events_bin["weight"].sum(), data_events_bin["weight"].sum()))

                signal_events.append(signal_events_bin)
                resonant_background_events.append(resonant_background_events_bin)
                background_events.append(background_events_bin)
                data_events.append(data_events_bin)

            if self.options["metric"] == "z_a":
                self.results[idx] = utils.calculate_za(signal_events, resonant_background_events, background_events, data_events, self.options)
                # FIXME: just using z_a calculation as a quick and dirty estimate. Need to replace with real fits + combine

            else:
                helper = combine_helper.CombineHelper(
                    options = self.options,
                    output_dir = self.output_dir + "/fits_" + self.output_tag,
                    signal_events = signal_events,
                    resonant_background_events = resonant_background_events,
                    background_events = background_events,
                    data_events = data_events
                )
                helper.run()
                self.results[idx] = helper.get_results()

        if self.options["metric"] == "z_a":
            best = {"Z_A_combined" : 0}
            for key, result in self.results.items():
                if result["Z_A_combined"] >= best["Z_A_combined"] and result["Bin_1"]["n_bkg"] > 0 and result["Bin_1"]["n_resonant_background"] > 0:
                    best = result

            self.results[-1] = best
            if self.debug > 1:
                print("[OptimizationHelper] Best binning combination", best)

        with open(self.output_dir + "/optimization_%s.json" % self.output_tag, "w") as f_out:
            json.dump(self.results, f_out, sort_keys = True, indent = 4)

    ########################
    ### Helper functions ###
    ########################

    def make_process_id_map(self):
        self.process_id_map = {}
        for sample, info in self.samples.items():
            self.process_id_map[sample] = info["process_id"]

        if self.debug > 0:
            print("[PrepHelper] process_id map: ", self.process_id_map)
        return

