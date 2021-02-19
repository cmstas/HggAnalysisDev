import os
import uproot
import awkward
import numpy
import glob
import json
import copy
import argparse

"""
This script takes in a json file of skimmed nanoAOD samples and calculates
metadata, including total number of events and scale1fb.
Outputs a new json file containing all of the original information plus scale1fb info.
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "path to input json",
    type = str,
    default = "../data/samples.json"
)
parser.add_argument(
    "--output",
    help = "path for output json",
    type = str,
    default = "../data/samples_and_scale1fb.json"
)
parser.add_argument(
    "--fast",
    help = "don't redo samples that are already present in output json",
    action = "store_true"
)
parser.add_argument(
    "--debug",
    help = "debug",
    type = int,
    default = 0
)
args = parser.parse_args()

### Helper Functions ###
def calc_scale1fb(xs, sum_weights):
    if xs <= 0:
        return -1
    else:
        return (xs * 1000.) / sum_weights

def calculate_metadata(files, xs, debug):
    nEvents = 0
    sumWeights = 0

    for file in files:
        f = uproot.open(file)
        runs = f["Runs"]

        nEvents_file = int(numpy.sum(runs["genEventCount"].array()))
        sumWeights_file = int(numpy.sum(runs["genEventSumw"].array()))

        nEvents += nEvents_file 
        sumWeights += sumWeights_file 
        if debug > 0:
            print("[scale1fb.py: calculate_metadata] From file %s, got %d events and %.2f sum of weights" % (file, nEvents_file, sumWeights_file))

    scale1fb = calc_scale1fb(xs, sumWeights)

    results = {
        "xs" : xs,
        "scale1fb" : scale1fb,
        "n_events" : nEvents,
        "sumWeights" : sumWeights
    }
    return results

### Main script ###
if args.debug > 0:
    print("[scale1fb.py] Running scale1fb.py with options:", args)
    
with open(args.input, "r") as f_in:
    samples = json.load(f_in)

output = copy.deepcopy(samples)

if args.fast and os.path.exists(args.output):
    print("[scale1fb.py] Fast option selected and existing output file found, will only recalculate metadata for samples that aren't present in output.")
    with open(args.output, "r") as f_in:
        original_output = json.load(f_in)

    for sample, info in output.items():
        if sample in original_output.keys():
            for year, year_info in original_output[sample].items():
                if "201" not in year:
                    continue
                if "metadata" in year_info.keys():
                    if "scale1fb" in year_info["metadata"].keys():
                        output[sample][year] = original_output[sample][year]

for sample, info in samples.items():
    if sample.lower() == "data":
        continue

    for year, year_info in info.items():
        if "201" not in year:
            continue # skip non-year sample metadata
        # Grab metadata
        files = []
        for path in year_info["paths"]:
            files += glob.glob(path + "/*.root")
            files += glob.glob(path + "/*/*/*/*.root") # to be compatible with CRAB

        if "xs" not in year_info["metadata"].keys():
            if args.debug > 0:
                print("[scale1fb.py] Sample: %s, year %s, does not have a xs value, only grabbing events and weights." % (sample, year))
            xs = -1
        else:
            xs = year_info["metadata"]["xs"]

        if len(files) == 0:
            if args.debug > 0:
                print("[scale1fb.py] Sample: %s, year %s, does not have any files found, skipping."  % (sample, year))
            continue


        if args.fast:
            if sample in original_output.keys():
                if year in original_output[sample].keys():
                    if "metadata" in original_output[sample][year].keys():
                        if "scale1fb" in original_output[sample][year]["metadata"].keys():
                            if args.debug > 0:
                                print("[scale1fb.py] Sample: %s, year %s already has previous scale1fb info, skipping" % (sample, year))
                            continue
    
        metadata = calculate_metadata(files, xs, args.debug)
        
        if args.debug > 0:
            print("[scale1fb.py] Grabbed metadata for sample %s, year %s, as " % (sample, year), metadata)

        # Add to output json
        for field in metadata:
            if field not in output[sample][year]["metadata"]:
                output[sample][year]["metadata"][field] = metadata[field]

# Write output json
with open(args.output, "w") as f_out:
    json.dump(output, f_out, sort_keys = True, indent = 4)
