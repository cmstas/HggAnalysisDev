import awkward as ak
import json

br_bb = 0.5824
br_TT = 0.0627
br_WW = 0.2137
br_gg = 0.0023

br_ggbb = br_gg * br_bb * 2
br_ggWW = br_gg * br_WW * 2
br_ggTT = br_gg * br_TT * 2

df = ak.from_parquet('~/HiggsDNA/BSM_13Oct22/merged_nominal.parquet')

with open('/home/users/iareed/HiggsDNA/BSM_13Oct22/summary.json') as f_in:
    summary = json.load(f_in)

sample_id_map = summary['sample_id_map']

bb_keys = ['2HDM_bb_M250','2HDM_bb_M300','2HDM_bb_M350']
WW_keys = ['2HDM_WW_M250','2HDM_WW_M300','2HDM_WW_M350']
TT_keys = ['2HDM_TAUTAU_M250','2HDM_TAUTAU_M300','2HDM_TAUTAU_M350']

def scale_weight (df, id_map, key_list, scale_value):
    for key in key_list:
        tmp_mask = df.process_id==id_map[key]
        #multi_mask = ak.ones_like(df.weight_central)
        #multi_mask = ak.where(tmp_mask, scale_value, multi_mask)
        print("----------------")
        print(df[tmp_mask].weight_central)
        df['weight_central'] = ak.where(tmp_mask, df.weight_central * scale_value, df.weight_central)
        print(df[tmp_mask].weight_central)

scale_weight(df, sample_id_map, bb_keys, br_ggbb)
scale_weight(df, sample_id_map, WW_keys, br_ggWW)
scale_weight(df, sample_id_map, TT_keys, br_ggTT)

ak.to_parquet(df,'/home/users/iareed/HiggsDNA/BSM_13Oct22/fixed_2HDM_weight/merged_nominal.parquet')

