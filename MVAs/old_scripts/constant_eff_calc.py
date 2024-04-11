import awkward as ak
import json

tag = 'no_stop'
blind = True
input_dir = 'output/higgs_cand_'+tag+'_mva_scored_df.parquet'
if blind:
    tag += '_blind'
print(tag)

sum_path = 'higgs_cand_no_stop/summary.json'

df = ak.from_parquet(input_dir)
with open(sum_path) as f_in:
    process_map = json.load(f_in)['sample_id_map']

#print(process_map)

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
    'procs': ['DiPhoton',  'GJets_HT-40To100','GJets_HT-100To200', 'GJets_HT-200To400', 'GJets_HT-400To600', 'GJets_HT-600ToInf', 'TTGG', 'TTGamma', 'TTJets', 'WGamma', 'ZGamma'],
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
signal_mask = (df.process_id == process_map['ttHH_ggbb']) | (df.process_id == process_map['ttHH_ggWW']) | (df.process_id == process_map['ttHH_ggTauTau'])
signal_df = df[signal_mask]

total_signal = ak.sum(signal_df.weight_central)
print(total_signal)
#print(ak.sum(signal_df.weight_central[signal_df.mva_score>=0.9903]))
#print(ak.sum(signal_df.weight_central[signal_df.mva_score>=0.9903])/total_signal)
#print(ak.sum(signal_df.weight_central[signal_df.mva_score>=0.908545]))
#print(ak.sum(signal_df.weight_central[signal_df.mva_score>=0.908545])/total_signal)
SR1_eff_thres = 0.3952
SR2_eff_thres = 0.7813
close_enough = 0.0005

good_thres_1 = False
good_thres_2 = False

SR1_bin=0.9999
decrement = 0.0001
increment = 0.000001
while not good_thres_1:
    test_mask = signal_df.mva_score >= SR1_bin
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

while not good_thres_2:
    test_mask = signal_df.mva_score >= SR2_bin
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

#SR1_bin = 0.9904
#SR2_bin = 0.9090

header = 'tag; bin_1; bin_2;'
vals = tag+'; {:.4f}; {:.4f};'.format(SR1_bin, SR2_bin)
ind_header = ''
ind_vals = ''
print(header)
print(vals)
if blind:
    low_mass_mask = df.Diphoton_mass >= 120
    high_mass_mask = df.Diphoton_mass <= 130
    mass_mask = (low_mass_mask) & (high_mass_mask)
    mass_mask = ~mass_mask
    exceptions = ak.zeros_like(df.process_id)
    for proc in signal['procs']:
        print(proc, process_map[proc])
        exceptions = ak.where(df.process_id == process_map[proc], 1, exceptions)
    for proc in res['procs']:
        print(proc, process_map[proc])
        exceptions = ak.where(df.process_id == process_map[proc], 1, exceptions)
    exceptions = ak.where(exceptions == 1, True, False)

    df = df[mass_mask | exceptions]


for proc in process_map:
    tmp_mask = df.process_id == process_map[proc]
    tmp_df = df[tmp_mask]
    tmp_tot = ak.sum(tmp_df.weight_central)
    ind_header += proc + '_pre; '
    ind_vals += '{:.4f};'.format(tmp_tot)
    print('After preselection, {} has {:.2f} events'.format(proc,tmp_tot))
    SR1_mask = tmp_df.mva_score >= SR1_bin
    SR1_tot = ak.sum(tmp_df.weight_central[SR1_mask])
    SR1_eff = SR1_tot/tmp_tot*100
    SR2_mask = tmp_df.mva_score >= SR2_bin
    SR2_tot = ak.sum(tmp_df.weight_central[SR2_mask])
    SR2_eff = SR2_tot/tmp_tot*100
    ind_header += proc + '_SR1; '
    ind_vals += '{:.4f};'.format(SR1_tot)
    ind_header += proc + '_SR2; '
    ind_vals += '{:.4f};'.format(SR2_tot)
    print('SR1 has {:.2f} events, {:.2f}% eff'.format(SR1_tot, SR1_eff))
    print('SR2 has {:.2f} events, {:.2f}% eff'.format(SR2_tot, SR2_eff))
    if proc in signal['procs']:
        signal['pre_tot'] += tmp_tot
        signal['SR1_tot'] += SR1_tot
        signal['SR2_tot'] += SR2_tot
    elif proc in res['procs']:
        res['pre_tot'] += tmp_tot
        res['SR1_tot'] += SR1_tot
        res['SR2_tot'] += SR2_tot
    elif proc in nonres['procs']:
        nonres['pre_tot'] += tmp_tot
        nonres['SR1_tot'] += SR1_tot
        nonres['SR2_tot'] += SR2_tot
    else:
        data['pre_tot'] += tmp_tot
        data['SR1_tot'] += SR1_tot
        data['SR2_tot'] += SR2_tot

def combined_saver(group, name, titles, values):
    for field in group:
        if field == 'procs':
            continue
        titles += name + '_' + field + ';'
        values += '{:.4f};'.format(group[field])
    return titles, values

header, vals = combined_saver(signal, 'signal', header, vals)
header, vals = combined_saver(res, 'res', header, vals)
header, vals = combined_saver(nonres, 'nonres', header, vals)
header, vals = combined_saver(data, 'data', header, vals)
header += ind_header
vals += ind_vals

#with open('compare.csv', 'a') as out:
#    out.writelines([header+'\n', vals+'\n'])


