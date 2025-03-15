import pandas as pd
import csv
from nba_api.stats.endpoints import PlayerGameLog
from nba_api.stats.static import players
import time

file_name = "data.csv"

columns = ['Player_ID', 'WL', 'MIN', 'POINTS', 'REBOUNDS', 'ASSISTS', 'STEALS', 'BLOCKS', 
           'PLUS_MINUS', 'TOV', 'FGM', 'FG_PCT', 'FG3M','FG3_PCT', 'FTM', 'FT_PCT', 'OPP TEAM', 'COURT', 'BTB']

with open(file_name, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(columns)  

active_players = players.get_active_players()
player_ids = [player["id"] for player in active_players]

for player_id in player_ids[:1]:
    time.sleep(1)
    season = "2023-24"

    game_log = PlayerGameLog(player_id=player_id, season=season)
    df = game_log.get_data_frames()[0]

    df = df[['Player_ID', 'WL', 'MIN', 'POINTS', 'REBOUNDS', 'ASSISTS', 'STEALS', 'BLOCKS', 
           'PLUS_MINUS', 'TOV', 'FGM', 'FG_PCT', 'FG3M','FG3_PCT', 'FTM', 'FT_PCT', 'OPP TEAM', 'COURT', 'BTB']]
    
    df['COURT'] = df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')
    df.loc[df['COURT'] == "Home", 'MATCHUP'] = df['MATCHUP'].str.split('vs.').str[1].str.strip()
    df.loc[df['COURT'] != "Home", 'MATCHUP'] = df['MATCHUP'].str.split('@').str[1].str.strip()

    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%b %d, %Y')
    df['NEXT_GAME_DATE'] = df['GAME_DATE'].shift(-1)
    df['BTB'] = (df['GAME_DATE'] - df['NEXT_GAME_DATE']).dt.days == 1

    df.rename(columns={
        'PTS': 'POINTS', 
        'REB': 'REBOUNDS', 
        'AST': 'ASSISTS', 
        'MATCHUP': 'OPP TEAM', 
        'STL': 'STEALS', 
        'BLK': 'BLOCKS',
        'BTB': 'BACK TO BACK',
    }, inplace=True)

    df[columns].to_csv(file_name, mode="a", header=False, index=False)

    print("PLAYER_ID: " + str(player_id) + " DONE")
