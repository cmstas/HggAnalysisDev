import pandas as pd

df = pd.read_pickle("../Preselection/output/HHggbb_Presel_HggAD_comparison.pkl")
df.to_parquet("../Preselection/output/HHggbb_Presel_HggAD_comparison.parquet")
