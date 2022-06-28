import os
import root_numpy
import numpy

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input", help = "input df", type=str, default = "/home/users/smay/Hgg/HggAnalysisDev/MVAs/output/test_finalfit_df.npz")
args = parser.parse_args()

events = numpy.load(args.input, allow_pickle=True)["events"]
output = args.input.split("/")[-1].replace(".npz", ".root")
os.system("rm %s" % output)
root_numpy.array2root(events, output, treename="t")
