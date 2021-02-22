import argparse

from helpers import zip_helper 

"""
This script takes in an ntuple and one or more mvas and
evaluates their scores, zipping the score into a new ntuple,
retaining a specified subset of branches from the original ntuple.
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "path to input dataframe",
    type = str,
    default = "../Preselection/output/HHggTauTau_InclusivePresel_SyncWithFranny.pkl"
)
parser.add_argument(
    "--mvas",
    help = "csv list of path to jsons containing mvas to zip in ntuple",
    type = str,
    default = "output/test.json"
)
parser.add_argument(
    "--names",
    help = "csv list of names to save mva scores as",
    type = str,
    default = "mva_score"
)
parser.add_argument(
    "--output",
    help = "name of output dataframe",
    type = str,
    default = "output/test_finalfit_df.pkl"
)
parser.add_argument(
    "--debug",
    help = "debug level",
    type = int,
    default = 0
)

args = parser.parse_args()
zipper = zip_helper.ZipHelper(**vars(args))
zipper.run()

