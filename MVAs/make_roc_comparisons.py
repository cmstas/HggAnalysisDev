import numpy
from sklearn import metrics

from helpers import utils

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--inputs", help = "csv list of which .npz files to consider", type=str)
parser.add_argument("--labels", help = "csv list of labels for each .npz file", type=str)
parser.add_argument("--log", help = "log axis for roc curve", action="store_true")
parser.add_argument("--output", help = "name of output pdf", type=str, default = "output/auc_comparison.pdf")
args = parser.parse_args()

inputs = (args.inputs.replace(" ","")).split(",")
labels = args.labels.split(",")

colors = ["black", "red", "blue", "green", "orange"]

files = []
for input in inputs:
  files.append(numpy.load(input))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111)

signal_effs = [0.25, 0.5, 0.9, 0.99]
effs = {}

for i in range(len(files)):
  if not "dnn_roc" in inputs[i]:
    fpr = files[i]["fpr_test"]
    tpr = files[i]["tpr_test"]
  else:
    fpr = files[i]["fpr_validation"]
    tpr = files[i]["tpr_validation"]

  tprs = []
  fprs = []
  for eff in signal_effs:
    sig_eff, idx = utils.find_nearest(tpr, eff)
    tprs.append(tpr[idx])
    fprs.append(fpr[idx])

  auc = metrics.auc(fpr, tpr)
  effs[labels[i]] = { "fpr" : fprs, "tpr" : tprs, "auc" : auc }

  ax1.plot(fpr, tpr, label = labels[i] + " [AUC = %.3f]" % (auc), color = colors[i])
  if "tpr_unc_test" in files[i].files:
      tpr_unc = files[i]["tpr_unc_test"]
      ax1.fill_between(fpr, tpr - 1*(tpr_unc/2.), tpr + 1*(tpr_unc/2.), color = colors[i], alpha = 0.25)


plt.ylim(0,1)
plt.xlim(0,1)

if args.log:
    plt.xlim(0.005, 1)
    if effs[labels[0]]["auc"] > 0.95:
        plt.xlim(0.0005, 1)
    ax1.set_xscale("log")

plt.xlabel('False Positive Rate (Background Efficiency)')
ax1.set_ylabel('True Positive Rate (Signal Efficiency)')
legend = ax1.legend(loc='lower right')
ax1.yaxis.set_ticks_position('both')
ax1.grid(True)
plt.savefig(args.output)

# Table
print("\\begin{center} \\Fontvi")
print("\\begin{tabular}{|c||c|c|c|c|c|}")
print("\\multicolumn{6}{c}{Performance Metrics} \\\\ \\hline \\hline")
print("\\multirow{3}{*}{Method} & \\multicolumn{5}{c|}{Metric (\\%)} \\\\ \\cline{2-6}")
print(" & \\multirow{2}{*}{AUC} & \\multicolumn{4}{c|}{Background efficiency at fixed signal efficiency} \\\\ \\cline{3-6}") 
print(" & & $\\epsilon_{\\text{bkg}} (\\epsilon_{\\text{sig}} = 25\\%)$ & $\\epsilon_{\\text{bkg}} (\\epsilon_{\\text{sig}} = 50\\%)$ & $\\epsilon_{\\text{bkg}} (\\epsilon_{\\text{sig}} = 90\\%)$ & $\\epsilon_{\\text{bkg}} (\\epsilon_{\\text{sig}} = 99\\%)$ \\\\ \\hline")
for method in list(effs.keys()):
  print(("%s & %.2f & %.2f & %.2f & %.2f & %.2f \\\\ \\hline" % (method, effs[method]["auc"] * 100, effs[method]["fpr"][0] * 100, effs[method]["fpr"][1] * 100, effs[method]["fpr"][2] * 100, effs[method]["fpr"][3] * 100)))

print("\\end{tabular} \\end{center}")
