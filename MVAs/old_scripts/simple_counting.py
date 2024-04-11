import awkward as ak
import json

d_in = 'GJets_2_scores_12Jul22/'
df = ak.from_parquet(d_in+'merged_nominal.parquet')
with open(d_in+'summary.json') as f_in:
    process_map = json.load(f_in)['sample_id_map']

high_mass_mask = df.Diphoton_mass >= 120
low_mass_mask = df.Diphoton_mass <= 130
mass_window_mask = high_mass_mask & low_mass_mask
bdf = df[~mass_window_mask]
#high_mass_mask = bdf.Diphoton_mass >= 120
#low_mass_mask = bdf.Diphoton_mass <= 130
#mass_window_mask = high_mass_mask & low_mass_mask
#print(ak.count_nonzero(bdf.Diphoton_mass[mass_window_mask]))
signal = {
    'procs': ['ttHH_ggbb', 'ttHH_ggWW', 'ttHH_ggTauTau'],
    'pre_tot': 0,
    'SR1_tot': 0,
    'SR2_tot': 0
}
res = {
    'procs': ['VBFH_M125', 'VH_M125', 'ggH_M125', 'ttH_M125'],
    'pre_tot': 0,
    'SR1_tot': 0,
    'SR2_tot': 0
}
nonres = {
#    'procs': ['DiPhoton', 'GJets/QCD(Data)', 'TTGG', 'TTGamma', 'TTJets', 'WGamma', 'ZGamma'],
    'procs': ['DiPhoton', 'GJets_HT-40To100','GJets_HT-100To200', 'GJets_HT-200To400', 'GJets_HT-400To600', 'GJets_HT-600ToInf', 'TTGG', 'TTGamma', 'TTJets', 'WGamma', 'ZGamma'],
    'pre_tot': 0,
    'SR1_tot': 0,
    'SR2_tot': 0
}
data = {
    'procs': ['Data'],
    'pre_tot': 0,
    'SR1_tot': 0,
    'SR2_tot': 0
}
def mask_maker(df, id_map, procs):
    tmp_mask = ak.zeros_like(df.process_id)
    for proc in procs:
        tmp_mask = ak.where(df.process_id==id_map[proc], 1, tmp_mask)
    tmp_mask = ak.where(tmp_mask==1,True,False)
    return tmp_mask

signal_mask = mask_maker(df, process_map, signal['procs'])
res_mask = mask_maker(bdf, process_map, res['procs'])
nonres_mask = mask_maker(bdf, process_map, nonres['procs'])
data_mask = mask_maker(bdf, process_map, data['procs'])

signal_df = df[signal_mask]
total_signal = ak.sum(signal_df.weight_central)
SR1_eff_thres = 0.35
#SR1_eff_thres = 0.3952
SR2_eff_thres = 0.7813
close_enough = 0.0005

good_thres_1 = False
good_thres_2 = False

SR1_bin=0.9999
decrement = 0.0001
increment = 0.000001
while not good_thres_1:
    test_mask = signal_df.stand_score >= SR1_bin
    total_test = ak.sum(signal_df.weight_central[test_mask])
    test_eff = total_test/total_signal
    diff = SR1_eff_thres - test_eff
    #print(SR1_bin, test_eff, diff)
    if abs(diff) < close_enough:
        good_thres_1 = True
    elif diff > 0:
        SR1_bin -= decrement
    else:
        SR1_bin += increment
print('Found SR1 bin edge at: {:.4f}'.format(SR1_bin))
   
SR2_bin = SR1_bin
SR2_bin -= 0.01
good_thres_2 = True

while not good_thres_2:
    test_mask = signal_df.stand_score >= SR2_bin
    total_test = ak.sum(signal_df.weight_central[test_mask])
    test_eff = total_test/total_signal
    diff = SR2_eff_thres - test_eff
    #print(SR2_bin, test_eff, diff)
    if abs(diff) < close_enough:
        good_thres_2 = True
    elif diff > 0:
        SR2_bin -= decrement
    else:
        SR2_bin += increment
print('Found SR2 bin edge at: {:.4f}'.format(SR2_bin))

SR1_mask = bdf.stand_score >= SR1_bin
SR1_sig_mask = df.stand_score >= SR1_bin
SR2_mask_inclusive = bdf.stand_score >= SR2_bin
SR2_mask = SR2_mask_inclusive & ~SR1_mask

print('signal Total SR1: {:.4f}'.format(ak.sum(df.weight_central[signal_mask & SR1_sig_mask])))
print('res Total SR1: {:.4f}'.format(ak.sum(bdf.weight_central[res_mask & SR1_mask])))
print('nonres Total SR1: {:.4f}'.format(ak.sum(bdf.weight_central[nonres_mask & SR1_mask])))
print('data Total SR1: {:.4f}'.format(ak.sum(bdf.weight_central[data_mask & SR1_mask])))



