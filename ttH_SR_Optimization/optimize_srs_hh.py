import os, sys
import json
import numpy

sys.path.append("~/ttH/Binning/")
import guided_optimizer_hh as guided_optimizer

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", help = "tag to distinguish this optimization", type=str, default = "test")
parser.add_argument("--channel", help = "leptonic or hadronic", type=str, default = "Hadronic")
parser.add_argument("--file", help = "path to final fit tree", type=str)
parser.add_argument("--coupling", help = "coupling (Hut or Hct)", type=str)
parser.add_argument("--mvas", help = "list of mva branches to perform Nd optimization with", type=str, default = "mva_score")
parser.add_argument("--sm_higgs_unc", help = "value of unc on sm higgs processes", type=float, default = 0.1)
parser.add_argument("--nCores", help = "number of cores to use", type=int, default = 18)
parser.add_argument("--bins", help = "csv list of number of bins", type=str, default = "1,2,3,4,5")
parser.add_argument("--metric", help = "optimize upper limit or significance", type=str, default = "limit")
parser.add_argument("--pt_selection", help = "cut on dipho_pt", type=str, default="")
args = parser.parse_args()

mvas = args.mvas.split(",")
dim = len(mvas)
mva_dict = { str(dim) + "d" : mvas }

bins = [int(a) for a in args.bins.split(",")]

if args.metric == "limit":
    combineOption = 'AsymptoticLimits -m 125 --expectSignal=0'
elif args.metric == "upper limit":
    combineOption = 'AsymptoticLimits -m 125 --expectSignal=1'
elif args.metric == "significance":
    combineOption = 'Significance --expectSignal=1 '
elif args.metric == "cl":
    combineOption = 'MultiDimFit --algo=singles --expectSignal=1'

optimizer = guided_optimizer.Guided_Optimizer(
                input = args.file,
                tag = args.tag,
                channel = args.channel,
                coupling = args.coupling,
                nCores = args.nCores,

                sm_higgs_unc = args.sm_higgs_unc,
                combineOption = combineOption,
                pt_selection = args.pt_selection,

                n_bins = bins,
                mvas = mva_dict,
                strategies = ['guided'],
               
                initial_points = 36,
                points_per_epoch = 36,
                n_epochs = 5,
                verbose = True
)

optimizer.optimize()
