import pandas as pd

df = pd.read_pickle("output/HH_ggXX_df.pkl")
df.to_parquet("output/HH_ggXX_df.parquet")
