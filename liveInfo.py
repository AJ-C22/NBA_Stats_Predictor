from nba_api.stats.endpoints import CommonPlayerInfo, ScoreboardV2
from nba_api.stats.static import players, teams
from datetime import datetime

player = "Lebron James"
today = datetime.today().strftime('%Y-%m-%d')

scoreboard = ScoreboardV2(game_date=today)

games = scoreboard.get_dict()["resultSets"][0]["rowSet"]

live_games = []
for game in games:
    game_id = game[2] 
    home_team = game[6]  
    away_team = game[7]  
    game_status = game[4].strip()
    
    home_team_info = teams.find_team_name_by_id(home_team)
    home_team_name = home_team_info['abbreviation']
    away_team_info = teams.find_team_name_by_id(away_team)
    away_team_name = away_team_info['abbreviation']
    live_games.append({
        "Game ID": game_id,
        "Home Team": home_team_name,
        "Away Team": away_team_name,
        "Status": game_status
    })

for game in live_games:
    print(game)

player_info = players.find_players_by_full_name(player)
player_id = player_info[0]['id']

player_info = CommonPlayerInfo(player_id=player_id)
team_name = player_info.get_dict()['resultSets'][0]['rowSet'][0][20]

opp_team = ''
court = ''
for game in live_games:
    if game['Home Team'].strip() == team_name.strip():
        opp_team = game['Away Team']
        court = "Home"
    elif game['Away Team'].strip() == team_name.strip():
        opp_team = game['Home Team']
        court = "Away"
        
if opp_team != '':
    print(team_name + " vs. " + opp_team)        