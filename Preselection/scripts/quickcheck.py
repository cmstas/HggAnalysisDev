import uproot
import awkward as ak
import numpy as np
import pandas as pd

#fname = "/hadoop/cms/store/user/hmei/Hgg/sync_diphoton/testntuple_from_microaod_withSyst.root"
#f = uproot.open(fname)
#t = f["ttHLeptonicTagDumper/trees/tth_13TeV_GeneralDipho"]
#
#df = t.arrays(["event", "dipho_mass"], library="pd") 
#
#print (len(df))
#
#nevents_noOverlap = np.count_nonzero( np.unique(df["event"].to_numpy(), return_counts=True)[1] == 1 ) 
#print (nevents_noOverlap)

fname_bbgg_fgg = "/hadoop/cms/store/user/hmei/Hgg/sync_diphoton/testntuple_bbgg.root"
f_bbgg_fgg = uproot.open(fname_bbgg_fgg)
evt_list_fgg = np.array([])
for i in range(12):
    treename = f"test_13TeV_DoubleHTag_{i}"
    t = f_bbgg_fgg[f"tagsDumper/trees/{treename}"]
    df = t.arrays(["event"], library="pd")
    print (df.columns)
    evt_list_tmp = df["event"].to_numpy()

    evt_list_fgg = np.concatenate((evt_list_fgg, evt_list_tmp))

print (f"total events end up in SR of HIG-19-018: {len(evt_list_fgg)}")

df_bbgg_boost_inc = pd.read_pickle(
    "/home/users/azecchin/Analysis/HggAnalysisDev/MVAs/output/OverlapTest_inclusive.pkl")
df_bbgg_boost_350 = pd.read_pickle(
    "/home/users/azecchin/Analysis/HggAnalysisDev/MVAs/output/OverlapTest_350GeV.pkl")

boosted_inc = df_bbgg_boost_inc["genBBfromH_delta_R"] <= 0.8
boosted_350 = df_bbgg_boost_350["genBBfromH_delta_R"] <= 0.8

df_boosted_inc = df_bbgg_boost_inc[boosted_inc]
df_boosted_350 = df_bbgg_boost_350[boosted_350]

sel_inc = df_bbgg_boost_inc["mva_score"] > 0.962256 
df_bbgg_boost_inc_SR = df_bbgg_boost_inc[sel_inc]
df_boosted_inc_SR = df_bbgg_boost_inc[boosted_inc & sel_inc]

sel_350 = df_bbgg_boost_350["mva_score"] > 0.983240
df_bbgg_boost_350_SR = df_bbgg_boost_350[sel_350]
df_boosted_350_SR = df_bbgg_boost_350[boosted_350 & sel_350]


print(
    f"total events passing pre-sel (inclusive): {len(df_bbgg_boost_inc)/3} \n    of which boosted : {len(df_boosted_inc)/3}, frac {len(df_boosted_inc)/len(df_bbgg_boost_inc)}")
print (f"total events passing SR (inclusive): {len(df_bbgg_boost_inc_SR)/3} \n    of which boosted : {len(df_boosted_inc_SR)/3}, frac {len(df_boosted_inc_SR)/len(df_bbgg_boost_inc_SR)}")

print(
    f"total events passing pre-sel (350): {len(df_bbgg_boost_350)/3} \n    of which boosted : {len(df_boosted_350)/3}, frac {len(df_boosted_350)/len(df_bbgg_boost_350)}")
print (f"total events passing SR (350): {len(df_bbgg_boost_350_SR)/3} \n    of which boosted : {len(df_boosted_350_SR)/3}, frac {len(df_boosted_350_SR)/len(df_bbgg_boost_350_SR)}")
print ("\n")
n_overlap_inc_pre = len(np.intersect1d(evt_list_fgg, df_bbgg_boost_inc['event'].to_numpy()))
n_overlap_inc_pre_boosted = len(np.intersect1d(evt_list_fgg, df_boosted_inc['event'].to_numpy()))
n_overlap_350_pre = len(np.intersect1d(evt_list_fgg, df_bbgg_boost_350['event'].to_numpy()))
n_overlap_350_pre_boosted = len(np.intersect1d(evt_list_fgg, df_boosted_350['event'].to_numpy()))
n_overlap_inc_SR = len(np.intersect1d(evt_list_fgg, df_bbgg_boost_inc_SR['event'].to_numpy()))
n_overlap_inc_SR_boosted = len(np.intersect1d(evt_list_fgg, df_boosted_inc_SR['event'].to_numpy()))
n_overlap_350_SR = len(np.intersect1d(evt_list_fgg, df_bbgg_boost_350_SR['event'].to_numpy()))
n_overlap_350_SR_boosted = len(np.intersect1d(evt_list_fgg, df_boosted_350_SR['event'].to_numpy()))

print (f"overlap at pre-sel (inc): {n_overlap_inc_pre}, frac: { n_overlap_inc_pre / len(df_bbgg_boost_inc) * 3}")
print (f"   of which boosted: {n_overlap_inc_pre_boosted}, frac: { n_overlap_inc_pre_boosted/ len(df_boosted_inc) *3}")
print (f"overlap at SR (inc): {n_overlap_inc_SR}, frac: { n_overlap_inc_SR / len(df_bbgg_boost_inc_SR) * 3}")
print (f"   of which boosted: {n_overlap_inc_SR_boosted}, frac: { n_overlap_inc_SR_boosted/ len(df_boosted_inc_SR) *3}")
print (f"overlap at pre-sel (350): {n_overlap_350_pre}, frac: { n_overlap_350_pre / len(df_bbgg_boost_350) * 3}")
print (f"   of which boosted: {n_overlap_350_pre_boosted}, frac: { n_overlap_350_pre_boosted/ len(df_boosted_350) *3}")
print (f"overlap at SR (350): {n_overlap_350_SR}, frac: { n_overlap_350_SR / len(df_bbgg_boost_350_SR)* 3}")
print (f"   of which boosted: {n_overlap_350_SR_boosted}, frac: { n_overlap_350_SR_boosted/ len(df_boosted_350_SR) *3}")

#print (f"overlap list: {np.intersect1d(evt_list_fgg, df_bbgg_boost_inc['event'].to_numpy())}")
#print (f"double counting: { np.unique(df_bbgg_boost_inc['event'].to_numpy(), return_counts=True)}") 
#print (f"double counting: { np.unique(np.intersect1d(evt_list_fgg, df_bbgg_boost_350_SR['event'].to_numpy()), return_counts=True)}") 
