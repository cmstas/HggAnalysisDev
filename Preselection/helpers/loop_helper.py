import os
import json
import glob
import uproot
import pandas
import numpy
import awkward
import multiprocessing
import time
import copy

from selections import diphoton_selections, analysis_selections
from selections import photon_selections, lepton_selections, tau_selections, jet_selections, gen_selections

class LoopHelper():
    """
    Class to perform all looping activities: looping through samples,
    filling histograms, making data/MC plots, yield tables,
    writing a single ntuple with all events, etc
    """

    def __init__(self, **kwargs):
        self.samples = kwargs.get("samples")
        self.selections = kwargs.get("selections")
        self.options = kwargs.get("options")
        self.systematics = kwargs.get("systematics")
        self.years = kwargs.get("years").split(",")
        self.select_samples = kwargs.get("select_samples")
        if self.select_samples != "all":
            self.select_samples = self.select_samples.split(",")

        self.output_tag = kwargs.get("output_tag")
        self.output_dir = kwargs.get("output_dir")
        os.system("mkdir -p %s" % self.output_dir)

        self.batch = kwargs.get("batch")
        self.nCores = kwargs.get("nCores")
        self.debug = kwargs.get("debug")
        self.fast = kwargs.get("fast")
        self.dry_run = kwargs.get("dry_run")

        self.lumi_map = { "2016" : 35.9, "2017" : 41.5, "2018" : 59.8 }

        self.outputs = []

        if self.debug > 0:
            print("[LoopHelper] Creating LoopHelper instance with options:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in kwargs.items()]))

        with open(self.options, "r") as f_in:
            options = json.load(f_in)
            for key, info in options.items():
                setattr(self, key, info)

        self.save_branches += ["process_id", "weight", "year"]

        self.branches_data = [branch for branch in self.branches if "gen" not in branch]
        self.save_branches_data = [branch for branch in self.save_branches if "gen" not in branch]

        if self.debug > 0:
            print("[LoopHelper] Opening options file: %s" % self.options)
            print("[LoopHelper] Options loaded as:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in options.items()]))

        self.load_samples()

    def load_samples(self):
        with open(self.samples, "r") as f_in:
            self.samples_dict = json.load(f_in)

        if self.debug > 0:
            print("[LoopHelper] Running over the following samples:")
            print("\n".join(["{0}={1!r}".format(a, b) for a, b in self.samples_dict.items()]))

    ##########################
    ### Main function: run ###
    ##########################

    def run(self):
        self.prepare_jobs()     # split files for each job, prepare relevants inputs (scale1fb, isData, etc)

        start = time.time()
        self.submit_jobs()      # actually submit the jobs (local, Dask, condor)
        elapsed_time = time.time() - start
        print("[LoopHelper] Total time to run %d jobs on %d cores: %.2f minutes" % (len(self.jobs_manager), self.nCores, elapsed_time/60.))

        start = time.time()
        self.merge_outputs()    # merge individual pkl files into a single master pkl
        self.clean_up()
        elapsed_time = time.time() - start
        print("[LoopHelper] Total time to merge %d outputs: %.2f minutes" % (len(self.outputs), elapsed_time/60.))

        self.write_summary()    # write a json file containing run options

    ##################
    ### Core tasks ###
    ##################

    def prepare_jobs(self):
        self.jobs_manager = []

        for sample, info in self.samples_dict.items():
            if self.select_samples != "all":
                if sample not in self.select_samples:
                    continue

            if self.debug > 0:
                print("[LoopHelper] Running over sample: %s" % sample)
                print("[LoopHelper] details: ", info)

            for year, year_info in info.items():
                files = []
                if year not in self.years:
                    continue
                for path in year_info["paths"]:
                    files += glob.glob(path + "/*.root")
                    files += glob.glob(path + "/*/*/*/*.root") # to be compatible with CRAB

                if len(files) == 0:
                    continue

                job_info = {
                    "sample" : sample,
                    "process_id" : info["process_id"],
                    "year" : year,
                    "scale1fb" : 1 if sample == "Data" else year_info["metadata"]["scale1fb"],
                    "lumi" : self.lumi_map[year],
                    "resonant" : info["resonant"]
                }

                file_splits = self.chunks(files, info["fpo"])
                job_id = 0
                for file_split in file_splits:
                    job_id += 1
                    if self.fast:
                        if job_id > 1:
                            if self.debug > 0:
                                print("[LoopHelper] --fast option selected, only looping over 1 file for sample: %s (%s)" % (sample, year))
                            break
                    output = self.output_dir + self.selections + "_" + self.output_tag + "_" + sample + "_" + year + "_" + str(job_id) + ".pkl"
                    self.jobs_manager.append({
                        "info" : job_info,
                        "output" : output,
                        "files" : file_split
                    })
                    self.outputs.append(output)
        return

    def submit_jobs(self):
        if self.batch == "local":
            if self.debug > 0:
                print("[LoopHelper] Submitting %d jobs locally on %d cores" % (len(self.jobs_manager), self.nCores))

            manager = multiprocessing.Manager()
            running_procs = []
            for job in self.jobs_manager:
                if self.dry_run:
                    continue
                print(job)
                running_procs.append(multiprocessing.Process(target = self.loop_sample, args = (job,)))
                running_procs[-1].start()

                while True:
                    do_break = False
                    for i in range(len(running_procs)):
                        if not running_procs[i].is_alive():
                            running_procs.pop(i)
                            do_break = True
                            break
                        if len(running_procs) < self.nCores: # if we have less than nCores jobs running, break infinite loop and add another
                            do_break = True
                            break
                        else:
                            os.system("sleep 5s")
                    if do_break:
                        break

            while len(running_procs) > 0:
                for i in range(len(running_procs)):
                    try:
                        if not running_procs[i].is_alive():
                            running_procs.pop(i)
                    except:
                        continue

            return

        elif self.batch == "dask":
            return
            #TODO
        elif self.batch == "condor":
            return
            #TODO

    def merge_outputs(self):
        master_file = self.output_dir + self.selections + "_" + self.output_tag +  ".pkl"
        master_df = pandas.DataFrame()
        for file in self.outputs:
            if self.debug > 0:
                print("[LoopHelper] Loading file %s" % file)
            if not os.path.exists(file):
                continue
            df = pandas.read_pickle(file)
            master_df = pandas.concat([master_df, df], ignore_index=True)

        master_df.to_pickle(master_file)

    def clean_up(self):
        for file in self.outputs:
            if not os.path.exists(file):
                continue
            os.system("rm %s" % file)

    def write_summary(self):
        summary_file = self.output_dir + self.selections + "_" + self.output_tag + ".json"
        summary = vars(self)
        with open(summary_file, "w") as f_out:
            json.dump(summary, f_out, sort_keys = True, indent = 4)

    ################################
    ### Physics: selections, etc ###
    ################################

    def select_events(self, events, photons, metadata):
        options = copy.deepcopy(self.selection_options)
        for key, value in metadata.items(): # add sample-specific options to selection options
            options[key] = value

        # Diphoton preselection: NOTE we assume diphoton preselection is common to every analysis
        diphoton_events = events # most of dipho preselection already applied, still need to enforce pt/mgg and mgg cuts
        selected_photons = photon_selections.create_selected_photons(photons, self.branches, self.debug) # create record manually since it doesn't seem to work for selectedPhoton
        diphoton_events, selected_photons = diphoton_selections.diphoton_preselection(diphoton_events, selected_photons, options, self.debug)

        events_and_objects = {}

        if self.selections == "HHggTauTau_InclusivePresel":
            if "genZStudy" in self.selections:
                gen_events = diphoton_events.GenPart
            else:
                gen_events = None
            selected_events = analysis_selections.ggTauTau_inclusive_preselection(diphoton_events, selected_photons, diphoton_events.Electron, diphoton_events.Muon, diphoton_events.Tau, diphoton_events.Jet, diphoton_events.dR, gen_events, options, self.debug)

        elif self.selections == "ttH_LeptonicPresel":
            selected_events = analysis_selections.tth_leptonic_preselection(diphoton_events, selected_photons, diphoton_events.Electron, diphoton_events.Muon, diphoton_events.Jet, options, self.debug)

        elif self.selections == "ttH_HadronicPresel":
            selected_events = analysis_selections.tth_hadronic_preselection(diphoton_events, selected_photons, diphoton_events.Electron, diphoton_events.Muon, diphoton_events.Jet, options, self.debug)

        elif self.selections== "ttH_InclusivePresel":
            selected_events = analysis_selections.tth_inclusive_preselection(diphoton_events, selected_photons, diphoton_events.Electron, diphoton_events.Muon, diphoton_events.Jet, options, self.debug)

        elif self.selections == "HHggbb_Presel":
            options["boosted"] = False
            selected_events = analysis_selections.ggbb_preselection(diphoton_events, selected_photons, diphoton_events.Electron, diphoton_events.Muon, diphoton_events.Jet, diphoton_events.FatJet, options, self.debug)

        elif self.selections == "HHggbb_boosted_Presel":
            options["boosted"] = True
            selected_events = analysis_selections.ggbb_preselection(diphoton_events, selected_photons, diphoton_events.Electron, diphoton_events.Muon, diphoton_events.Jet, diphoton_events.FatJet, options, self.debug)

        else:
            print("[LoopHelper] Selection: %s is not currently implemented, please check." % self.selections)
            return

        return selected_events

    def trim_events(self, events, data):
        if data:
            branches = self.save_branches_data
        else:
            branches = self.save_branches
        trimmed_events = events[branches]
        return trimmed_events

    def loop_sample(self, job):
        info = job["info"]
        sample = info["sample"]
        files = job["files"]
        output = job["output"]

        if sample == "Data":
            data = True
        else:
            data = False

        selection_metadata = {
            "resonant": info["resonant"],
            "data": data,
            "year": int(job["info"]["year"])
        }

        if self.debug > 0:
            print("[LoopHelper] Running job with parameters", job)

        sel_evts = []
        process_id = info["process_id"]

        for file in files:
            if self.debug > 0:
                print("[LoopHelper] Loading file %s" % file)

            events, photons = self.load_file(file, selection_metadata)
            if events is None:
                self.outputs.pop(output)
                return
            events = self.select_events(events, photons, selection_metadata)

            events["process_id"] = numpy.ones(len(events)) * process_id
            if data:
                events["weight"] = numpy.ones(len(events))
            else:
                events["weight"] = events.genWeight * info["scale1fb"] * info["lumi"]

            events["year"] = numpy.ones(len(events)) * int(info["year"])

            trimmed_events = self.trim_events(events, data) # drop unneeded branches
            sel_evts.append(trimmed_events)

        events_full = awkward.concatenate(sel_evts)
        self.write_to_df(events_full, output)
        return

    ########################
    ### Helper functions ###
    ########################

    def load_file(self, file, metadata, tree_name = "Events"):
        with uproot.open(file) as f:
            if not f:
                print("[LoopHelper] Problem opening file %s" % file)
                return None
            tree = f[tree_name]
            if not tree:
                print("[LoopHelper] Problem opening file %s" % file)
                return None

            if metadata["data"]:
                branches = self.branches_data
            else:
                branches = self.branches
            branches_no_pho = [branch for branch in branches if "selectedPhoton" not in branch]

            if metadata["data"]:
                if metadata["year"] == 2016:
                    triggers = ["HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"]
                if metadata["year"] == 2017:
                    triggers = ["HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"]
                if metadata["year"] == 2018:
                    triggers = ["HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"]
                branches_no_pho += triggers


            events = tree.arrays(branches_no_pho, library = "ak", how = "zip")

            branches_pho = [branch for branch in branches if "selectedPhoton" in branch]
            photons = tree.arrays(branches_pho, library = "ak", how = "zip")

            # library = "ak" to load arrays as awkward arrays for best performance
            # how = "zip" allows us to access arrays as records, e.g. events.Photon
        return events, photons

    def chunks(self, files, fpo):
        for i in range(0, len(files), fpo):
            yield files[i : i + fpo]

    def write_to_df(self, events, output_name):
        df = awkward.to_pandas(events)
        df.to_pickle(output_name)
        return
