import pandas as pd
import csv
from nba_api.stats.endpoints import PlayerGameLog
from nba_api.stats.static import players, teams


active_players = players.get_active_players()

print(active_players[0])


player_id = 201939  # Stephen Curry
season = "2022-23"

game_log = PlayerGameLog(player_id=player_id, season=season)
df = game_log.get_data_frames()[0]
#df.to_csv("data.csv", index=False)

df = df[['Player_ID','GAME_DATE', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 'TOV', 'FGM', 'FG3M', 'MATCHUP', 'MIN']]

df['COURT'] = df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')

df.loc[df['COURT'] == "Home", 'MATCHUP'] = df['MATCHUP'].str.split('vs.').str[1].str.strip()
df.loc[df['COURT'] != "Home", 'MATCHUP'] = df['MATCHUP'].str.split('@').str[1].str.strip()

df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
df['NEXT_GAME_DATE'] = df['GAME_DATE'].shift(-1)
df['BTB'] = (df['GAME_DATE'] - df['NEXT_GAME_DATE'] ).dt.days == 1

df.rename(columns={'PTS': 'POINTS', 'REB': 'REBOUNDS', 'AST': 'ASSISTS', 'MATCHUP': 'OPP TEAM', 'STL' : 'STEALS', 'BLK': 'BLOCKS'}, inplace=True)

df[['Player_ID', 'POINTS', 'REBOUNDS', 'ASSISTS', 'STEALS', 'BLOCKS','PLUS_MINUS','TOV','FGM','FG3M', 'OPP TEAM', 'COURT', 'BTB']].to_csv("data.csv", index=False)

print("CSV file written successfully!")
