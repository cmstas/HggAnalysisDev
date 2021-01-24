import argparse

from helpers import mva_helper

"""
This script writes events to an hdf5 file for BDT/DNN training.
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    help = "path to input hdf5",
    type = str,
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

args = parser.parse_args()

trainer = mva_helper.MVAHelper(**vars(args))
trainer.run()
