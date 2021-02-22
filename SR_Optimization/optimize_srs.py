import argparse

from helpers import optimization_helper

"""
This script takes a dataframe and scans N-d cuts on n signal regions to optimize
a specified metric (significance, upper limit, etc)
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "path to input dataframe",
    type = str,
    default = "../MVAs/output/test_finalfit_df.pkl"
)
parser.add_argument(
    "--debug",
    help = "debug level",
    type = int,
    default = 0
)
parser.add_argument(
    "--output_dir",
    help = "directory to save fits and combine results in",
    type = str,
    default = "output/"
)
parser.add_argument(
    "--output_tag",
    help = "tag to identify this optimization",
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
    "--samples",
    help = "json file containing list of samples (so we can match names to process id)",
    type = str,
    default = "../Preselection/data/samples_and_scale1fb.json"
)
parser.add_argument(
    "--metric",
    help = "metric to optimize (significance, upper limit, etc)",
    type = str,
    default = "significance"
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

args = parser.parse_args()

optimizer = optimization_helper.OptimizationHelper(**vars(args))
optimizer.run()
