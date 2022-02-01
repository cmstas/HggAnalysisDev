import pandas as pd
import numpy as np

df = pd.read_pickle("Dual_score_HH_ggXX_df.pkl")
print(df)

ttHH_SR = df['ttHH_score'] < .9971

filtered_df = df[ttHH_SR]

filtered_df.to_pickle("Filtered_HH_ggXX_df.pkl")
