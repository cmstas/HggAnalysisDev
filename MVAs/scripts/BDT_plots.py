import xgboost
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json

bdt_file="/home/users/iareed/HggAnalysisDev/MVAs/SM_23Sep22_full/SM_23Sep22_full.xgb"
df = pd.read_parquet("/home/users/iareed/HggAnalysisDev/MVAs/SM_23Sep22_full/merged_nominal.parquet") 

feature_list="/home/users/iareed/HggAnalysisDev/MVAs/data/ttHH_BDT_with_HHggXX.json"
with open("/home/users/iareed/HggAnalysisDev/MVAs/SM_23Sep22_full/summary.json","r") as f_in:
    config = json.load(f_in)
sampleId = config["sample_id_map"]

bdt_features = {
    "f0":"Diphoton_eta",
    "f1":"Diphoton_pt_mgg",
    "f2":"Diphoton_dR",
    "f3":"Diphoton_helicity",
    "f4":"LeadPhoton_mvaID",
    "f5":"SubleadPhoton_mvaID",
    "f6":"LeadPhoton_eta",
    "f7":"SubleadPhoton_eta",
    "f8":"LeadPhoton_pixelSeed",
    "f9":"SubleadPhoton_pixelSeed",
    "f10":"LeadPhoton_pt_mgg",
    "f11":"SubleadPhoton_pt_mgg",
    "f12":"ditau_pt",
    "f13":"ditau_eta",
    "f14":"ditau_mass",
    "f15":"ditau_dR",
    "f16":"ditau_helicity",
    "f17":"MET_pt",
    "f18":"n_jets",
    "f19":"n_leptons",
    "f20":"n_electrons",
    "f21":"n_muons",
    "f22":"n_taus",
    "f23":"jet_1_pt",
    "f24":"jet_1_eta",
    "f25":"jet_1_btagDeepFlavB",
    "f26":"jet_2_pt",
    "f27":"jet_2_eta",
    "f28":"jet_2_btagDeepFlavB",
    "f29":"jet_3_pt",
    "f30":"jet_3_eta",
    "f31":"jet_3_btagDeepFlavB",
    "f32":"jet_4_pt",
    "f33":"jet_4_eta",
    "f34":"jet_4_btagDeepFlavB",
    "f35":"jet_5_pt",
    "f36":"jet_5_eta",
    "f37":"jet_5_btagDeepFlavB",
    "f38":"jet_6_pt",
    "f39":"jet_6_eta",
    "f40":"jet_6_btagDeepFlavB",
    "f41":"b_jet_1_btagDeepFlavB",
    "f42":"b_jet_2_btagDeepFlavB",
    "f43":"b_jet_3_btagDeepFlavB",
    "f44":"b_jet_4_btagDeepFlavB",
    "f45":"lepton_1_pt",
    "f46":"lepton_1_eta",
    "f47":"lepton_1_mass",
    "f48":"lepton_1_charge",
    "f49":"lepton_1_id",
    "f50":"lepton_2_pt",
    "f51":"lepton_2_eta",
    "f52":"lepton_2_mass",
    "f53":"lepton_2_charge",
    "f54":"lepton_2_id",
    "f55":"lepton_3_pt",
    "f56":"lepton_3_eta",
    "f57":"lepton_3_mass",
    "f58":"lepton_3_charge",
    "f59":"lepton_3_id",
    "f60":"costhetastar_cs_HHggbb",
    "f61":"costheta_bb",
    "f62":"costheta_gg",
    "f63":"costheta_TauTau",
    "f64":"costhetastar_cs_HHggTauTau",
    "f65":"Dijet_pt",
    "f66":"Dijet_eta",
    "f67":"Dijet_mass",
    "f68":"Dijet_score",
    "f69":"pt_gg_Mggjj",
    "f70":"pt_jj_Mggjj",
    "f71":"Mx"
}

bdt = xgboost.Booster()
bdt.load_model(bdt_file)

feature_imp = bdt.get_score(importance_type='gain')
keys = [bdt_features[k] for k in feature_imp.keys()]
values = list(feature_imp.values())

data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by ="score",ascending=False)
plt.figure()
data.nlargest(40, columns="score").plot(kind='barh', figsize = (20,20)) 
plot_name = "output/gain_40.png"
plt.savefig(plot_name)

# calculate the correlation matrix #TODO produce that for signal and bkg
signals= ["ttHH_ggbb",  "ttHH_ggWW", "ttHH_ggTauTau"]
backgrounds= ["DiPhoton","TTGamma","TTGG","WGamma","ZGamma","TTJets",
"ggH_M125","VBFH_M125","VH_M125","ttH_M125","DataDrivenGJets",
"HHggbb","HHggTauTau","HHggWW_dileptonic","HHggWW_semileptonic"
    ]

df_sig= df.loc[df['process_id'].isin([sampleId[proc] for proc in  signals])]
df_bkg= df.loc[df['process_id'].isin([sampleId[proc] for proc in  backgrounds])]
df_sig = df_sig[bdt_features.values()].copy()
df_bkg = df_bkg[bdt_features.values()].copy()
corr_sig = df_sig.corr()

plt.figure(figsize=(15, 15), dpi=240)

# plot the heatmap
sns.heatmap(corr_sig, 
        xticklabels=corr_sig.columns,
        yticklabels=corr_sig.columns)

plt.savefig("output/corr_matrix_sig.png")

corr_bkg = df_bkg.corr()

plt.figure(figsize=(15, 15), dpi=240)

# plot the heatmap
sns.heatmap(corr_bkg, 
        xticklabels=corr_bkg.columns,
        yticklabels=corr_bkg.columns)

plt.savefig("output/corr_matrix_bkg.png")
