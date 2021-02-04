import json
import argparse

from helpers import loop_helper

"""
This script is an all-purpose looper which performs a selection and writes
all events passing this selection to a pandas dataframe
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
    default = "2016,2017,2018"
)
parser.add_argument(
    "--select_samples",
    help = "csv list of samples to run over (should be a subset of samples in args.samples)",
    type = str,
    default = "all"
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
parser.add_argument( #TODO
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
parser.add_argument(
    "--output_dir",
    help = "dir to place outputs in", 
    type = str,
    default = "output/"
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
parser.add_argument(
    "--dry_run",
    help = "don't submit jobs",
    action = "store_true"
)

args = parser.parse_args()

looper = loop_helper.LoopHelper(**vars(args))
looper.run()
