import os
import root_numpy
import numpy
import numpy.lib.recfunctions as rcf

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input", help = "input df", type=str, default = "/home/users/smay/Hgg/HggAnalysisDev/MVAs/output/test_finalfit_df.npz")
# parser.add_argument("--debug", help = "input df", type=str, default = "/home/users/smay/Hgg/HggAnalysisDev/MVAs/output/test_finalfit_df.npz")
args = parser.parse_args()

with numpy.load(args.input,allow_pickle = True) as in_numpy:
    events = in_numpy["events"]
    print ("[Numpy_2_root] numpy df loaded")
events = rcf.rename_fields(events,{"pt_gg/m_ggjj" : "pt_gg_Mggjj", "pt_jj/m_ggjj":"pt_jj_Mggjj"})
output = args.input.split("/")[-1].replace(".npz", ".root")
os.system("rm %s" % output)
print ("[Numpy_2_root] writing root files")
root_numpy.array2root(events, output, treename="t")
print ("[Numpy_2_root] All good")