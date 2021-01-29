import json
import argparse

from helpers import loop_helper

"""
This script is an all-purpose looper. Can perform any subset of the
following tasks:
    - loop over events and write to histograms/ntuple
    - make data/MC plots from histograms/ntuple
    - make yield tables from histograms/ntuple
"""

parser = argparse.ArgumentParser()

# Physics content
parser.add_argument(
    "--samples",
    help = "path to json file containing samples & metadata",
    type = str,
    default = "data/samples_and_scale1fb.json"
)
parser.add_argument(
    "--selections",
    help = "preselection(s) to perform looping for",
    type = str,
    default = "HHggTauTau_InclusivePresel"
)
parser.add_argument(
    "--years",
    help = "csv list of years",
    type = str,
    default = "2018"
)

# --options points to a json file containing options for looping
# this could include things like additional scaling of bkg samples,
# application of reweighting procedures, etc
parser.add_argument(
    "--options",
    help = "path to json file containing looping options",
    type = str,
    default = "data/HH_ggTauTau_default.json"
)
parser.add_argument(
    "--systematics",
    help = "include systematics variations", 
    action = "store_true"
)

# Book-keeping
parser.add_argument(
    "--output_tag",
    help = "tag to identify these plots/tables/ntuples",
    type = str,
    default = "test"
)

# Technical
parser.add_argument(
    "--batch",
    help = "run locally vs. on dask vs. condor",
    type = str,
    default = "local"
)
parser.add_argument(
    "--nCores",
    help = "number of cores to run locally on",
    type = int,
    default = 8
)
parser.add_argument(
    "--debug",
    help = "debug level",
    type = int,
    default = 0
)
parser.add_argument(
    "--fast",
    help = "loop over minimal set of samples (for debugging purposes)",
    action = "store_true"
)

# Output options
parser.add_argument(
    "--do_plots",
    help = "make data/MC plots", 
    action = "store_true"
)
parser.add_argument(
    "--do_tables",
    help = "make yield tables", 
    action = "store_true"
)
parser.add_argument(
    "--do_ntuple",
    help = "make single ntuple with all events",
    action = "store_true"
)

args = parser.parse_args()

looper = loop_helper.LoopHelper(**vars(args))
looper.run()
