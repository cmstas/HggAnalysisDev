import awkward as ak

# Name of df to cut down for FlashggFinalFit
tag = 'tagger_test'
# TODO: Auto pull bins from optimization limit
bdt_cuts = [0.9889,0.875688]

df = ak.from_parquet(tag + '/merged_nominal.parquet')

n_signal_regions = len(bdt_cuts)
sr_cuts = []
for i in range(n_signal_regions):
    cut_sr = df.mva_score >= bdt_cuts[i]
    for j in range(len(sr_cuts)):
        cut_sr = cut_sr & ~(sr_cuts[j])

    df['pass_sr_%d' % i] = cut_sr
    sr_cuts.append(cut_sr)

print(len(df.weight_central))
final_cut = df.Diphoton_mass < 0
for cut in sr_cuts:
    final_cut = final_cut | cut
srs = df[final_cut]
print(len(srs.weight_central))

ak.to_parquet(srs, tag + '/signal_regions.paruqet')
