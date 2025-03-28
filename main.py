import pandas as pd
import csv
import time
from nba_api.stats.endpoints import PlayerGameLog, BoxScoreAdvancedV2, leaguedashteamstats, TeamEstimatedMetrics
from nba_api.stats.static import players, teams

file_name = "2023-2024_pt3.csv"
columns = [
    # Player stats
    'PLAYER_NAME', 'MIN', 'POINTS', 'REBOUNDS', 'ASSISTS', 'STEALS', 'BLOCKS', 'USG_PCT', 
    
    # Player rolling averages
    'MINUTES_5GAME_AVG', 'POINTS_5GAME_AVG', 'REBOUNDS_5GAME_AVG', 'ASSISTS_5GAME_AVG', 
    'STEALS_5GAME_AVG', 'BLOCKS_5GAME_AVG',
    
    # Opponent and game context
    'OPP_TEAM', 'COURT', 'BTB', 
    
    # Player's team stats
    'TEAM_E_OFF_RATING', 'TEAM_E_DEF_RATING', 'TEAM_E_PACE',
    
    # Opponent's team stats
    'OPP_E_OFF_RATING', 'OPP_E_DEF_RATING', 'OPP_E_PACE'
]

all_teams = teams.get_teams()
team_dict = {team['abbreviation']: team['id'] for team in all_teams}

with open(file_name, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(columns)

active_players = players.get_active_players()
player_ids = [player["id"] for player in active_players]
count = 0
for player_id in player_ids:
    try:
        count += 1
        player_info = players.find_player_by_id(player_id)
        player_name = player_info['full_name']
        
        time.sleep(3)
        season = "2023-24"
        game_log = PlayerGameLog(player_id=player_id, season=season)
        df = game_log.get_data_frames()[0]

        if df.empty:
            continue  

        # Select necessary columns
        df = df[['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 
                 'TOV', 'FGM', 'FG_PCT', 'FG3M', 'FG3_PCT', 'FTM', 'FT_PCT', 
                 'MATCHUP', 'GAME_DATE']]

        df['COURT'] = df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')
        df[['TEAM', 'OPP_TEAM']] = df['MATCHUP'].str.split(r'vs\.|@', regex=True, expand=True).apply(lambda x: x.str.strip())
        team_info = df['TEAM'].apply(lambda x: teams.find_team_by_abbreviation(x))
        opp_team_info = df['OPP_TEAM'].apply(lambda x: teams.find_team_by_abbreviation(x))
        df['TEAM_ID'] = team_info.apply(lambda x: x['id'] if isinstance(x, dict) else None)
        df['OPP_TEAM_ID'] = opp_team_info.apply(lambda x: x['id'] if isinstance(x, dict) else None)

        team_info = teams.find_team_by_abbreviation(df['TEAM'].iloc[0])  
        opp_team_info = teams.find_team_by_abbreviation(df['OPP_TEAM'].iloc[0])  
        team_id = team_info['id'] if team_info else None
        opp_team_id = opp_team_info['id'] if opp_team_info else None
        
                

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
        df['MINUTES_5GAME_AVG'] = df['MIN'].rolling(window=5).mean()

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
     
     # ------------------------------------
        
        advStatsFinder = TeamEstimatedMetrics(season=season)
        estStats = advStatsFinder.get_data_frames()[0]

        estStats = estStats[['TEAM_ID', 'E_OFF_RATING', 'E_DEF_RATING', 'E_NET_RATING', 'E_PACE']]

        advancedGamefinder = leaguedashteamstats.LeagueDashTeamStats(season=season)
        teamStats = advancedGamefinder.get_data_frames()[0]

        teamStats = teamStats[['TEAM_ID', 'TEAM_NAME', 'OREB_RANK', 'DREB_RANK', 'REB_RANK',  
                            'AST_RANK', 'STL_RANK', 'BLK_RANK', 'PTS_RANK', 'PLUS_MINUS_RANK']]

        merged_team_data = pd.merge(estStats, teamStats, on='TEAM_ID', how='inner')

        teamFinalStats = merged_team_data
        teamFinalStats = teamFinalStats.rename(columns={
            'E_OFF_RATING': 'TEAM_E_OFF_RATING', 
            'E_DEF_RATING': 'TEAM_E_DEF_RATING', 
            'E_PACE': 'TEAM_E_PACE',
   
        })
        oppTeamFinalStats = merged_team_data
        oppTeamFinalStats = oppTeamFinalStats.rename(columns={
            'E_OFF_RATING': 'OPP_E_OFF_RATING', 
            'E_DEF_RATING': 'OPP_E_DEF_RATING', 
            'E_PACE': 'OPP_E_PACE',
        })

    # -------------------------------------
        df = df.merge(teamFinalStats, left_on='TEAM_ID', right_on='TEAM_ID', how='left')
        df = df.merge(oppTeamFinalStats, left_on='OPP_TEAM_ID', right_on='TEAM_ID', how='left')

    # ---------------------------------------
        df[columns].to_csv(file_name, mode="a", header=False, index=False)
        
        print(f"{count}: PLAYER {player_name} DONE")
    
    except Exception as e:
        print(f"Error for {player_name}: {e}")
        player_ids.append(player_id)
        time.sleep(30)
