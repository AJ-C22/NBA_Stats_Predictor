import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats, TeamEstimatedMetrics

df1 = pd.read_csv('2023-2024_pt1.csv')
df2 = pd.read_csv('2023-2024_pt2.csv')
df3 = pd.read_csv('2023-2024_pt3.csv')

merged_df = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

merged_df.to_csv('2023-2024.csv', index=False)
