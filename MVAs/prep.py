import argparse

from helpers import prep_helper

"""
This script writes events to an hdf5 file for BDT/DNN training.
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "path to input dataframe",
    type = str,
    default = "../Preselection/output/HHggTauTau_InclusivePresel_v0.2_4Feb2021_SyncWithFranny.pkl"
)
parser.add_argument(
    "--debug",
    help = "debug level",
    type = int,
    default = 1
)
parser.add_argument(
    "--config",
    help = "json file with config options",
    type = str,
    default = "data/HH_ggTauTau_BaselineBDT.json"
)
parser.add_argument(
    "--output",
    help = "name of output hdf5 file",
    type = str,
    default = "output/test.hdf5"
)

args = parser.parse_args()

prepper = prep_helper.PrepHelper(**vars(args))
prepper.run()
