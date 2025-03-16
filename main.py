import pandas as pd
import csv
import time
from nba_api.stats.endpoints import PlayerGameLog, BoxScoreAdvancedV2
from nba_api.stats.static import players, teams

file_name = "data2.csv"
columns = [
    #ADD MORE ABOUT THE OPPOSING TEAM
    'Player_ID', 'PLAYER_NAME', 'WL', 'MIN', 'POINTS', 'REBOUNDS', 'ASSISTS', 'STEALS', 'BLOCKS', 
    'PLUS_MINUS', 'TOV', 'FGM', 'FG_PCT', 'FG3M', 'FG3_PCT', 'FTM', 'FT_PCT', 'OPP_TEAM', 'COURT', 'BTB',
    'USG_PCT', 'TS_PCT', 'PER', 'POINTS_5GAME_AVG', 'REBOUNDS_5GAME_AVG', 'ASSISTS_5GAME_AVG', 'STEALS_5GAME_AVG', 
    'BLOCKS_5GAME_AVG'
]
all_teams = teams.get_teams()
team_dict = {team['abbreviation']: team['id'] for team in all_teams}

with open(file_name, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(columns)

active_players = players.get_active_players()
player_ids = [player["id"] for player in active_players]

for player_id in player_ids:
    try:
        player_info = players.find_player_by_id(player_id)
        player_name = player_info['full_name']
        
        # Fetch game logs
        time.sleep(1)
        season = "2023-24"
        game_log = PlayerGameLog(player_id=player_id, season=season)
        df = game_log.get_data_frames()[0]

        if df.empty:
            continue  

        # Select necessary columns
        df = df[['Game_ID','Player_ID', 'WL', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'PLUS_MINUS', 
                 'TOV', 'FGM', 'FG_PCT', 'FG3M', 'FG3_PCT', 'FTM', 'FT_PCT', 'MATCHUP', 'GAME_DATE']]

        df['COURT'] = df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')
        df['OPP_TEAM'] = df['MATCHUP'].str.split('vs.|@').str[1].str.strip()

        # Convert game date
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%b %d, %Y')
        df['NEXT_GAME_DATE'] = df['GAME_DATE'].shift(-1)
        df['BTB'] = (df['GAME_DATE'] - df['NEXT_GAME_DATE']).dt.days == 1
        
        # Calculate Rolling Averages for the last 5 games
        df['POINTS_5GAME_AVG'] = df['PTS'].rolling(window=5).mean()
        df['REBOUNDS_5GAME_AVG'] = df['REB'].rolling(window=5).mean()
        df['ASSISTS_5GAME_AVG'] = df['AST'].rolling(window=5).mean()
        df['STEALS_5GAME_AVG'] = df['STL'].rolling(window=5).mean()
        df['BLOCKS_5GAME_AVG'] = df['BLK'].rolling(window=5).mean()

        # Advanced stats (Usage Rate, True Shooting %, PER)
        df['USG_PCT'] = round((df['FGM'] + df['FTM'] + df['TOV']) / df['MIN'] * 100, 2)
        df['TS_PCT'] = round(df['PTS'] / (2 * (df['FGM'] + 0.44 * df['FTM'])), 2)
        df['PER'] = round((df['PTS'] + df['REB'] + df['AST'] + df['STL'] + df['BLK']) / df['MIN'], 2)
        df['PLAYER_NAME'] = player_name

        # Rename Columns
        df.rename(columns={
            'PTS': 'POINTS', 
            'REB': 'REBOUNDS', 
            'AST': 'ASSISTS', 
            'STL': 'STEALS', 
            'BLK': 'BLOCKS',
        }, inplace=True)

        # Save to CSV
        df[columns].to_csv(file_name, mode="a", header=False, index=False)

        print(f"PLAYER {player_name} DONE")
    
    except Exception as e:
        print(f"Error for {player_name}: {e}")
