import awkward as ak
import numpy as np
from sklearn import metrics
import json
import matplotlib.pyplot as plt

d_in = 'GJets_2_scores_12Jul22/'

df = ak.from_parquet(d_in+'merged_nominal.parquet')
with open(d_in+'summary.json') as s_in:
    summary = json.load(s_in)
id_map = summary['sample_id_map']
signal_procs = ['ttHH_ggbb', 'ttHH_ggWW', 'ttHH_ggTauTau']
std_bkg_procs = ['DiPhoton', 'TTGG', 'TTGamma', 'TTJets', 'VBFH_M125', 'VH_M125', 'WGamma', 'ZGamma', 'ggH_M125', 'ttH_M125', 'GJets_HT-100To200', 'GJets_HT-200To400', 'GJets_HT-400To600', 'GJets_HT-40To100', 'GJets_HT-600ToInf']
dd_bkg_procs = ['DiPhoton', 'TTGG', 'TTGamma', 'TTJets', 'VBFH_M125', 'VH_M125', 'WGamma', 'ZGamma', 'ggH_M125', 'ttH_M125', 'GJets/QCD(Data)']

def mask_maker(df, id_map, procs):
    tmp_mask = ak.zeros_like(df.process_id)
    for proc in procs:
        tmp_mask = ak.where(df.process_id==id_map[proc], 1, tmp_mask)
    tmp_mask = ak.where(tmp_mask==1,True,False)
    return tmp_mask

# Keep only samples of interest
signal_mask = mask_maker(df, id_map, signal_procs)
std_bkg_mask = mask_maker(df, id_map, std_bkg_procs)
dd_bkg_mask = mask_maker(df, id_map, dd_bkg_procs)
mc_mask = signal_mask | std_bkg_mask | dd_bkg_mask
mc_df = df[mc_mask]

# Recompute masks
signal_mask = mask_maker(mc_df, id_map, signal_procs)
std_bkg_mask = mask_maker(mc_df, id_map, std_bkg_procs)
dd_bkg_mask = mask_maker(mc_df, id_map, dd_bkg_procs)

std_df = mc_df[signal_mask | std_bkg_mask]
dd_df = mc_df[signal_mask | dd_bkg_mask]

std_sig_mask = mask_maker(std_df, id_map, signal_procs)
dd_sig_mask = mask_maker(dd_df, id_map, signal_procs)

std_std_fpr, std_std_tpr, thresholds = metrics.roc_curve(std_sig_mask, std_df.stand_score, sample_weight=std_df.weight_central)
std_std_fpr = sorted(std_std_fpr)
std_std_tpr = sorted(std_std_tpr)
std_std_auc = metrics.auc(std_std_fpr,std_std_tpr)

std_dd_fpr, std_dd_tpr, thresholds = metrics.roc_curve(std_sig_mask, std_df.data_score, sample_weight=std_df.weight_central)
std_dd_fpr = sorted(std_dd_fpr)
std_dd_tpr = sorted(std_dd_tpr)
std_dd_auc = metrics.auc(std_dd_fpr,std_dd_tpr)

dd_std_fpr, dd_std_tpr, thresholds = metrics.roc_curve(dd_sig_mask, dd_df.stand_score, sample_weight=dd_df.weight_central)
dd_std_fpr = sorted(dd_std_fpr)
dd_std_tpr = sorted(dd_std_tpr)
dd_std_auc = metrics.auc(dd_std_fpr,dd_std_tpr)

dd_dd_fpr, dd_dd_tpr, thresholds = metrics.roc_curve(dd_sig_mask, dd_df.data_score, sample_weight=dd_df.weight_central)
dd_dd_fpr = sorted(dd_dd_fpr)
dd_dd_tpr = sorted(dd_dd_tpr)
dd_dd_auc = metrics.auc(dd_dd_fpr,dd_dd_tpr)

plt.plot(std_std_fpr, std_std_tpr, label='mc bkg, mc training: AUC={:.3f}'.format(std_std_auc))
plt.plot(std_dd_fpr, std_dd_tpr, label='mc bkg, dd training: AUC={:.3f}'.format(std_dd_auc))
plt.plot(dd_std_fpr, dd_std_tpr, label='dd bkg, mc training: AUC={:.3f}'.format(dd_std_auc))
plt.plot(dd_dd_fpr, dd_dd_tpr, label='dd bkg, dd training: AUC={:.3f}'.format(dd_dd_auc))
plt.legend()
plt.xscale('log')
plt.ylim(0,1)
plt.xlim(0.0005,1)
plt.ylabel('True Positive Rate (Signal Efficiency)')
plt.xlabel('False Positive Rate (Background Efficiency)')
plt.savefig('/home/users/iareed/public_html/test.png')

