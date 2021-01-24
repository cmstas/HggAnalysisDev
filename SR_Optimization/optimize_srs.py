import argparse

from helpers import optimization_helper

"""
This script takes an ntuple with  
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "path to input ntuple",
    type = str
)
parser.add_argument(
    "--debug",
    help = "debug level",
    type = int,
    default = 0
)
parser.add_argument(
    "--output_tag",
    help = "tag to identify this training",
    type = str,
    default = "test"
)
parser.add_argument(
    "--optimization_options",
    help = "options for the SR optimization",
    type = str,
    default = "data/default_options.json"
)
parser.add_argument(
    "--metric",
    help = "metric to optimize (significance, upper limit, etc)",
    type = str,
    default = "significance"
)

args = parser.parse_args()

optimizer = optimization_helper.OptimizationHelper(**vars(args))
optimizer.run()
