import pandas as pd
import csv
from nba_api.stats.endpoints import PlayerGameLog

player_id = 201939  # Stephen Curry
season = "2022-23"

game_log = PlayerGameLog(player_id=player_id, season=season)
df = game_log.get_data_frames()[0]
#df.to_csv("data.csv", index=False)

df = df[['GAME_DATE', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 'TOV', 'FGM', 'FG3M', 'MATCHUP', 'MIN']]

df['COURT'] = df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')

df.loc[df['COURT'] == "Home", 'MATCHUP'] = df['MATCHUP'].str.split('vs.').str[1].str.strip()
df.loc[df['COURT'] != "Home", 'MATCHUP'] = df['MATCHUP'].str.split('@').str[1].str.strip()


df.rename(columns={'PTS': 'POINTS', 'REB': 'REBOUNDS', 'AST': 'ASSISTS', 'MATCHUP': 'OPP TEAM', 'STL' : 'STEALS', 'BLK': 'BLOCKS'}, inplace=True)

df[['POINTS', 'REBOUNDS', 'ASSISTS', 'STEALS', 'BLOCKS','PLUS_MINUS','TOV','FGM','FG3M', 'OPP TEAM', 'COURT']].to_csv("data.csv", index=False)

print("CSV file written successfully!")
