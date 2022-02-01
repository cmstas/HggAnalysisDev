import pandas as pd
import numpy as np

df_ttHH = pd.read_pickle("output/ttHH_ggXX_extra_df.pkl")
df_HH = pd.read_pickle("output/HH_ggXX_df.pkl")

ttHH_SR = df_ttHH['mva_score'] > .9971
ttHH_id1 = df_ttHH['process_id'] == 11
ttHH_id2 = df_ttHH['process_id'] == 12
ttHH_id3 = df_ttHH['process_id'] == 13
ttHH_id = ttHH_id1 | ttHH_id2 | ttHH_id3

tgHH_id1 = df_HH['process_id'] == 1
tgHH_id2 = df_HH['process_id'] == 2
tgHH_id3 = df_HH['process_id'] == 21
tgHH_id4 = df_HH['process_id'] == 22
tgHH_id = tgHH_id1 | tgHH_id2 | tgHH_id3 | tgHH_id4


HH_SR = df_HH['mva_score'] > .9557
HH_id1 = df_HH['process_id'] == 18
HH_id2 = df_HH['process_id'] == 19
HH_id3 = df_HH['process_id'] == 20
HH_id = HH_id1 | HH_id2 | HH_id3

gHH_id1 = df_HH['process_id'] == 6
gHH_id2 = df_HH['process_id'] == 7
gHH_id3 = df_HH['process_id'] == 8
gHH_id4 = df_HH['process_id'] == 9
gHH_id = gHH_id1 | gHH_id2 | gHH_id3 | gHH_id4

df_ttHH_SR_tt = df_ttHH[ttHH_SR & ttHH_id]
print(df_ttHH_SR_tt.shape[0])
df_ttHH_SR_gg = df_ttHH[ttHH_SR & tgHH_id]
print(df_ttHH_SR_gg.shape[0])
df_tthh_SR = df_ttHH[ttHH_SR]
df_ttHH_tt = df_ttHH[ttHH_id]
df_HH_SR_tt = df_HH[HH_SR & HH_id]
print(df_HH_SR_tt.shape[0])
df_HH_SR_gg = df_HH[HH_SR & gHH_id]
print(df_HH_SR_gg.shape[0])
df_HH_SR = df_HH[HH_SR]
df_HH_tt = df_HH[HH_id]


Overlap_SR_tt = pd.merge(df_ttHH_SR_tt, df_HH_SR_tt, on=['Diphoton_mass', 'MET_pt', 'event'], how='inner')
print(Overlap_SR_tt.shape[0])
print("{}% overlap of ttHH in SRs".format(100*Overlap_SR_tt.shape[0]/df_ttHH_SR_tt.shape[0]))


Overlap_SR_gg = pd.merge(df_ttHH_SR_gg, df_HH_SR_gg, on=['Diphoton_mass', 'MET_pt', 'event'], how='inner')
print(Overlap_SR_gg.shape[0])
print("{}% overlap of ggHH in SRs".format(100*Overlap_SR_gg.shape[0]/df_HH_SR_gg.shape[0]))
