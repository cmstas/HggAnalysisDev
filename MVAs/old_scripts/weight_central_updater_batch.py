import awkward as ak
import json

br_bb = 0.5824
br_TT = 0.0627
br_WW = 0.2137
br_gg = 0.0023

br_ggbb = br_gg * br_bb * 2
br_ggWW = br_gg * br_WW * 2
br_ggTT = br_gg * br_TT * 2

df = ak.from_parquet('file_in')

print('Opening: file_in')
with open('/home/users/iareed/HiggsDNA/BSM_13Oct22/summary.json') as f_in:
    summary = json.load(f_in)

sample_id_map = summary['sample_id_map']

bb_keys = ['2HDM_bb_M250','2HDM_bb_M300','2HDM_bb_M350']
WW_keys = ['2HDM_WW_M250','2HDM_WW_M300','2HDM_WW_M350']
TT_keys = ['2HDM_TAUTAU_M250','2HDM_TAUTAU_M300','2HDM_TAUTAU_M350']

def scale_weight (df, id_map, key_list, scale_value):
    for key in key_list:
        tmp_mask = df.process_id==id_map[key]
        #print("----------------")
        #print(df[tmp_mask].weight_central)
        df['weight_central'] = ak.where(tmp_mask, df.weight_central * scale_value, df.weight_central)
        #print(df[tmp_mask].weight_central)

print('Reweighting bb')
scale_weight(df, sample_id_map, bb_keys, br_ggbb)
print('Reweighting WW')
scale_weight(df, sample_id_map, WW_keys, br_ggWW)
print('Reweighting TT')
scale_weight(df, sample_id_map, TT_keys, br_ggTT)


print('Saving: file_out')
ak.to_parquet(df,'file_out')

