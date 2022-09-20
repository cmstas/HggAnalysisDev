import awkward as ak
import json

#d_in = '2HDM_M250_26Jul22/'
d_in = '2HDM_M250_02Aug22/'
SR1_eff_thres = 0.5

print('Doing simple counting for {}'.format(d_in))
df = ak.from_parquet(d_in+'merged_nominal.parquet')
with open(d_in+'summary.json') as f_in:
    process_map = json.load(f_in)['sample_id_map']

high_mass_mask = df.Diphoton_mass >= 120
low_mass_mask = df.Diphoton_mass <= 130
mass_window_mask = high_mass_mask & low_mass_mask
mass_window_df = df[mass_window_mask]
sideband_df = df[~mass_window_mask]
M250_2HDM = {
    'procs': ['2HDM_M250'],
    'pre_tot': 0,
    'SR1_tot': 0,
    'SR2_tot': 0
}
sm = {
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

M250_2HDM_mask = mask_maker(mass_window_df, process_map, M250_2HDM['procs'])
sm_mask = mask_maker(mass_window_df, process_map, sm['procs'])
res_mask = mask_maker(mass_window_df, process_map, res['procs'])
nonres_mask = mask_maker(mass_window_df, process_map, nonres['procs'])
data_mask = mask_maker(sideband_df, process_map, data['procs'])

M250_2HDM_df = mass_window_df[M250_2HDM_mask]
total_M250_2HDM = ak.sum(M250_2HDM_df.weight_central)
#SR1_eff_thres = 0.3952
close_enough = 0.0005

good_thres_1 = False

SR1_bin=0.9999
decrement = 0.0001
increment = 0.000001
while not good_thres_1:
    test_mask = M250_2HDM_df.mva_score >= SR1_bin
    total_test = ak.sum(M250_2HDM_df.weight_central[test_mask])
    test_eff = total_test/total_M250_2HDM
    diff = SR1_eff_thres - test_eff
    #print(SR1_bin, test_eff, diff)
    if abs(diff) < close_enough:
        good_thres_1 = True
    elif diff > 0:
        SR1_bin -= decrement
    else:
        SR1_bin += increment
print('Tagert Signal Eff: {:.4f}, Found Signal Eff: {:.4f}'.format(SR1_eff_thres, test_eff))
print('Found SR1 bin edge at: {:.4f}'.format(SR1_bin))
   
SR1_mask = mass_window_df.mva_score >= SR1_bin
SR1_data_mask = sideband_df.mva_score >= SR1_bin

print('M250_2HDM Total SR1: {:.4f}'.format(ak.sum(mass_window_df.weight_central[M250_2HDM_mask & SR1_mask])))
print('sm Total SR1: {:.4f}'.format(ak.sum(mass_window_df.weight_central[sm_mask & SR1_mask])))
print('res Total SR1: {:.4f}'.format(ak.sum(mass_window_df.weight_central[res_mask & SR1_mask])))
print('nonres Total SR1: {:.4f}'.format(ak.sum(mass_window_df.weight_central[nonres_mask & SR1_mask])))
print('data Total SR1: {:.4f}'.format(ak.sum(sideband_df.weight_central[data_mask & SR1_data_mask])))

