import argparse

from helpers import mva_helper, tree_helper 

"""
This script takes in an ntuple and one or more mvas and
evaluates their scores, zipping the score into a new ntuple,
retaining a specified subset of branches from the original ntuple.
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "path to input ntuple",
    type = str
)
parser.add_argument(
    "--mvas",
    help = "path to json containing mvas to zip in ntuple",
    type = str,
)
parser.add_argument(
    "--branches",
    help = "csv list of branches to store in output ntuple",
    type = str,
    default = "weight,process_idx,process_name,event,run,lumi,year"
)
parser.add_argument(
    "--output",
    help = "name of output ntuple",
    type = str,
    default = "test.root"
)
parser.add_argument(
    "--debug",
    help = "debug level",
    type = int,
    default = 0
)

args = parser.parse_args()
tree_maker = tree_helper.TreeHelper(**vars(args))
tree_maker.run()

