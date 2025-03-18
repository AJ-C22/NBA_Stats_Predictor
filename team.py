import pandas as pd
from nba_api.stats.endpoints import leaguedashteamstats, TeamEstimatedMetrics

advStatsFinder = TeamEstimatedMetrics(season="2023-24")
estStats = advStatsFinder.get_data_frames()[0]

estStats = estStats[['TEAM_ID', 'E_OFF_RATING', 'E_DEF_RATING', 'E_NET_RATING', 'E_PACE']]


advancedGamefinder = leaguedashteamstats.LeagueDashTeamStats(season='2024-25')
teamStats = advancedGamefinder.get_data_frames()[0]

print("Available columns in LeagueDashTeamStats:", teamStats.columns)

teamStats = teamStats[['TEAM_ID', 'TEAM_NAME', 'OREB_RANK', 'DREB_RANK', 'REB_RANK',  
                       'AST_RANK', 'STL_RANK', 'BLK_RANK', 'PTS_RANK', 'PLUS_MINUS_RANK']]

merged_team_data = pd.merge(estStats, teamStats, on='TEAM_ID', how='inner')


csv_filename = "team_stats.csv"
merged_team_data.to_csv(csv_filename, index=False)
print(f"Saved team statistics to {csv_filename}")
