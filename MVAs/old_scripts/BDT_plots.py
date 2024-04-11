import xgboost
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json

bdt_file="/home/users/iareed/HggAnalysisDev/MVAs/output/2HDM_M350_25Sep23_fixed_dijets.xgb"
#bdt_file="/home/users/iareed/HggAnalysisDev/MVAs/output/SM_22Sep23_fixed_dijets.xgb"
plot_name = "output/gain_40_2HDM_M350.pdf"

df = pd.read_parquet("/home/users/iareed/HiggsDNA/Full_Samples_21Jun23/fixed_dijet_dummies/scored/merged_nominal.parquet")
#df = pd.read_parquet("/home/users/iareed/HggAnalysisDev/MVAs/output/SM_22Sep23_fixed_dijet_scored.parquet")

#feature_list="/home/users/iareed/HggAnalysisDev/MVAs/data/HiggsDNA_ttHH_no_lepton_mass.json"
with open("/home/users/iareed/HiggsDNA/Full_Samples_21Jun23/fixed_dijet_dummies/scored/summary.json","r") as f_in:
#with open("/home/users/iareed/HggAnalysisDev/MVAs/SM_23Sep22_full/summary.json","r") as f_in:
    config = json.load(f_in)
sampleId = config["sample_id_map"]

bdt_features = {
    "f0":"Diphoton_pt_mgg",
    "f1":"Diphoton_eta",
    "f2":"Diphoton_dR",
    "f3":"Diphoton_helicity",

    "f4":"LeadPhoton_pt_mgg",
    "f5":"LeadPhoton_eta",
    "f6":"LeadPhoton_mvaID",
    "f7":"LeadPhoton_pixelSeed",

    "f8":"SubleadPhoton_pt_mgg",
    "f9":"SubleadPhoton_eta",
    "f10":"SubleadPhoton_mvaID",
    "f11":"SubleadPhoton_pixelSeed",

    "f12":"MET_pt",

    "f13":"jet_1_pt",
    "f14":"jet_1_eta",
    "f15":"jet_1_btagDeepFlavB",

    "f16":"jet_2_pt",
    "f17":"jet_2_eta",
    "f18":"jet_2_btagDeepFlavB",

    "f19":"jet_3_pt",
    "f20":"jet_3_eta",
    "f21":"jet_3_btagDeepFlavB",

    "f22":"jet_4_pt",
    "f23":"jet_4_eta",
    "f24":"jet_4_btagDeepFlavB",

    "f25":"jet_5_pt",
    "f26":"jet_5_eta",
    "f27":"jet_5_btagDeepFlavB",

    "f28":"jet_6_pt",
    "f29":"jet_6_eta",
    "f30":"jet_6_btagDeepFlavB",

    "f31":"b_jet_1_btagDeepFlavB", 
    "f32":"b_jet_2_btagDeepFlavB", 
    "f33":"b_jet_3_btagDeepFlavB", 
    "f34":"b_jet_4_btagDeepFlavB",

    "f35":"Dijet_pt",
    "f36":"Dijet_eta",
    "f37":"Dijet_mass",
    "f38":"Dijet_score",

    "f39":"lepton_1_pt",
    "f40":"lepton_1_eta",
    "f41":"lepton_1_mass",
    "f42":"lepton_1_id",

    "f43":"lepton_2_pt",
    "f44":"lepton_2_eta",
    "f45":"lepton_2_charge",
    "f46":"lepton_2_id",

    "f47":"lepton_3_pt",
    "f48":"lepton_3_eta",
    "f49":"lepton_3_charge",
    "f50":"lepton_3_id",

    "f51":"n_jets",
    "f52":"n_leptons",
    "f53":"n_electrons",
    "f54":"n_muons",

    "f55":"Mx",
    "f56":"pt_gg_Mggjj",
    "f57":"pt_jj_Mggjj",

    "f58":"costhetastar_cs_HHggbb",
    "f59":"costheta_bb",
    "f60":"costheta_gg",
}

bdt = xgboost.Booster()
bdt.load_model(bdt_file)

feature_imp = bdt.get_score(importance_type='gain')
keys = [bdt_features[k] for k in feature_imp.keys()]
values = list(feature_imp.values())

data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by ="score",ascending=False)
plt.figure()
data.nlargest(40, columns="score").plot(kind='barh', figsize = (20,20)) 
#plot_name = "output/gain_40_bb.pdf"
plt.savefig(plot_name)
quit()
# calculate the correlation matrix #TODO produce that for signal and bkg
signals= ["Tprime_BB_M1500","Tprime_WW_M1500","Tprime_TAUTAU_M1500"]
backgrounds= ["ttHH_ggbb",  "ttHH_ggWW", "ttHH_ggTauTau","DiPhoton","TTGamma","TTGG","WGamma","ZGamma","TTJets",
"ggH_M125","VBFH_M125","VH_M125","ttH_M125","DataDrivenGJets",
"HHggbb","HHggTauTau","HHggWW_dileptonic","HHggWW_semileptonic"
    ]
#signals= ["ttHH_ggbb",  "ttHH_ggWW", "ttHH_ggTauTau"]
#backgrounds= ["DiPhoton","TTGamma","TTGG","WGamma","ZGamma","TTJets",
#"ggH_M125","VBFH_M125","VH_M125","ttH_M125","DataDrivenGJets",
#"HHggbb","HHggTauTau","HHggWW_dileptonic","HHggWW_semileptonic"
#    ]


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

plt.savefig("output/corr_matrix_sig_Tprime_M1500.png")

corr_bkg = df_bkg.corr()

plt.figure(figsize=(15, 15), dpi=240)

# plot the heatmap
sns.heatmap(corr_bkg, 
        xticklabels=corr_bkg.columns,
        yticklabels=corr_bkg.columns)

plt.savefig("output/corr_matrix_bkg_Tprime_M1500.png")
