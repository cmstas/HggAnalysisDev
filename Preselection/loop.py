import argparse

from helpers import loop_helper

parser = argparse.ArgumentParser()

# Physics content
parser.add_argument(
    "--samples",
    help = "path to json file containing samples & metadata",
    type = str,
    default = "data/samples.json"
)
parser.add_argument(
    "--selections",
    help = "preselection(s) to perform looping for",
    type = str,
    default = "HHggTauTau_InclusivePresel"
)
# --options points to a json file containing options for looping
# this could include things like additional scaling of bkg samples,
# application of reweighting procedures, etc
parser.add_argument(
    "--options",
    help = "path to json file containing looping options",
    type = str,
    default = "data/default.json"
)
parser.add_argument(
    "--systematics",
    help = "include systematics variations (True/False)",
    type = bool,
    default = False
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

# Output options
parser.add_argument(
    "--do_plots",
    help = "make data/MC plots (True/False)",
    type = bool,
    default = True
)
parser.add_argument(
    "--do_tables",
    help = "make yield tables (True/False)",
    type = bool,
    default = True
)
parser.add_argument(
    "--do_ntuple",
    help = "make single ntuple with all events",
    type = bool,
    default = True
)



args = parser.parse_args()

looper = loop_helper.LoopHelper(**vars(args))
looper.run()
