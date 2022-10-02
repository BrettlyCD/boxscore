#dynamic responses for specific game data

import requests as rq
import pandas as pd
import json
from json import loads
from tables import last_game_dict

#pull gameID from last game of favorite team
with open('_dicts.json') as f:
    data = json.load(f)
fave = int(data["faves"]['NHL'])
nhl_last_game = last_game_dict['gameID'][fave]


###need total box score by period###


#pull in 3 stars of the game
response = rq.get("https://statsapi.web.nhl.com/api/v1/game/" + str(nhl_last_game) + "/feed/live")
stars = pd.json_normalize(response.json())
stars = stars[['liveData.decisions.firstStar.fullName'
                    , 'liveData.decisions.secondStar.fullName'
                    , 'liveData.decisions.thirdStar.fullName']] #bring in only desired columns
threeStars = stars.rename(columns = {'liveData.decisions.firstStar.fullName': 'firstStar'
                    , 'liveData.decisions.secondStar.fullName': 'secondStar'
                    , 'liveData.decisions.thirdStar.fullName': 'thirdStar'}).transpose()
threeStars.rename(columns={0: 'Player'}, inplace = True)

#pull in team box score for the game
response = rq.get("https://statsapi.web.nhl.com/api/v1/game/" + str(nhl_last_game) + "/boxscore")
team = response.json()
df = pd.DataFrame(team['teams'])
#setup away team stats row
away_stats = pd.DataFrame(df.loc["teamStats","away"])
away_team = df.loc["team","away"]["name"]
away_stats.reset_index(inplace = True)
away_stats.rename(columns={'teamSkaterStats': away_team, 'index': 'Stat'}, inplace = True)
#setup home team stats row
home_stats = pd.DataFrame(df.loc["teamStats","home"])
home_team = df.loc["team","home"]["name"]
home_stats.reset_index(inplace = True)
home_stats.rename(columns={'teamSkaterStats': home_team, 'index': 'Stat'}, inplace = True)
#union the two tables together
game_stats = pd.merge(home_stats,
    away_stats,
    how = "outer",
    on = "Stat"
    )
game_stats.set_index('Stat', inplace = True)
summary_stats = game_stats.reindex(["goals","shots","pim","hits","takeaways","giveaways","blocked","faceOffWinPercentage","powerPlayGoals","powerPlayOpportunities","powerPlayPercentage"])

#pull in player stats for the game
response = rq.get("https://statsapi.web.nhl.com/api/v1/game/" + str(nhl_last_game) + "/boxscore")
team = response.json()
df = pd.DataFrame(team['teams'])
#setup away team skater stats
away_player_stats = pd.DataFrame(df.loc["players","away"])
away_player_json = away_player_stats.transpose().to_json(orient = 'records')
away_player_stats = pd.json_normalize(loads(away_player_json))
away_skater_stats = away_player_stats[away_player_stats['position.abbreviation'] != 'G']
away_skater_stats = away_skater_stats[['jerseyNumber', 'person.fullName','position.abbreviation','stats.skaterStats.timeOnIce','stats.skaterStats.goals','stats.skaterStats.assists','stats.skaterStats.plusMinus','stats.skaterStats.shots','stats.skaterStats.hits','stats.skaterStats.blocked','stats.skaterStats.penaltyMinutes','stats.skaterStats.faceOffPct','stats.skaterStats.takeaways','stats.skaterStats.giveaways']]
away_skater_stats.rename(columns={'jerseyNumber': '#', 'person.fullName': 'Skater','position.abbreviation': 'Position','stats.skaterStats.timeOnIce': 'TOI','stats.skaterStats.goals': 'Goals','stats.skaterStats.assists': 'Assists','stats.skaterStats.plusMinus': '+-','stats.skaterStats.shots': 'Shots','stats.skaterStats.hits': 'Hits','stats.skaterStats.blocked': 'Blocks','stats.skaterStats.penaltyMinutes': 'PIM','stats.skaterStats.faceOffPct': 'FO%','stats.skaterStats.takeaways': 'TKA','stats.skaterStats.giveaways': 'GVA'}, inplace = True)
away_skater_stats.set_index('#', inplace = True)
#setup home team skater stats
home_player_stats = pd.DataFrame(df.loc["players","home"])
home_player_json = home_player_stats.transpose().to_json(orient = 'records')
home_player_stats = pd.json_normalize(loads(home_player_json))
home_skater_stats = home_player_stats[home_player_stats['position.abbreviation'] != 'G']
home_skater_stats = home_skater_stats[['jerseyNumber', 'person.fullName','position.abbreviation','stats.skaterStats.timeOnIce','stats.skaterStats.goals','stats.skaterStats.assists','stats.skaterStats.plusMinus','stats.skaterStats.shots','stats.skaterStats.hits','stats.skaterStats.blocked','stats.skaterStats.penaltyMinutes','stats.skaterStats.faceOffPct','stats.skaterStats.takeaways','stats.skaterStats.giveaways']]
home_skater_stats.rename(columns={'jerseyNumber': '#', 'person.fullName': 'Skater','position.abbreviation': 'Position','stats.skaterStats.timeOnIce': 'TOI','stats.skaterStats.goals': 'Goals','stats.skaterStats.assists': 'Assists','stats.skaterStats.plusMinus': '+-','stats.skaterStats.shots': 'Shots','stats.skaterStats.hits': 'Hits','stats.skaterStats.blocked': 'Blocks','stats.skaterStats.penaltyMinutes': 'PIM','stats.skaterStats.faceOffPct': 'FO%','stats.skaterStats.takeaways': 'TKA','stats.skaterStats.giveaways': 'GVA'}, inplace = True)
home_skater_stats.set_index('#', inplace = True)

#setup away team goalie stats
away_goalie_stats = away_player_stats[away_player_stats['position.abbreviation'] == 'G']
away_goalie_stats = away_goalie_stats[['jerseyNumber', 'person.fullName','position.abbreviation','stats.goalieStats.saves','stats.goalieStats.shots','stats.goalieStats.powerPlaySaves','stats.goalieStats.powerPlayShotsAgainst']]
away_goalie_stats.rename(columns={'jerseyNumber': '#', 'person.fullName': 'Player','position.abbreviation': "Position",'stats.goalieStats.saves': 'Saves','stats.goalieStats.shots': 'Shots','stats.goalieStats.powerPlaySaves': 'PPSaves','stats.goalieStats.powerPlayShotsAgainst': 'PPShots'}, inplace = True)
away_goalie_stats['Save%'] = (away_goalie_stats.Saves / away_goalie_stats.Shots)
away_goalie_stats['PPS%'] = (away_goalie_stats.PPSaves / away_goalie_stats.PPShots)
away_goalie_stats.set_index('#', inplace = True)
#setup home team goalie stats
home_goalie_stats = home_player_stats[home_player_stats['position.abbreviation'] == 'G']
home_goalie_stats = home_goalie_stats[['jerseyNumber', 'person.fullName','position.abbreviation','stats.goalieStats.saves','stats.goalieStats.shots','stats.goalieStats.powerPlaySaves','stats.goalieStats.powerPlayShotsAgainst']]
home_goalie_stats.rename(columns={'jerseyNumber': '#', 'person.fullName': 'Player','position.abbreviation': "Position",'stats.goalieStats.saves': 'Saves','stats.goalieStats.shots': 'Shots','stats.goalieStats.powerPlaySaves': 'PPSaves','stats.goalieStats.powerPlayShotsAgainst': 'PPShots'}, inplace = True)
home_goalie_stats['Save%'] = (home_goalie_stats.Saves / home_goalie_stats.Shots)
home_goalie_stats['PPS%'] = (home_goalie_stats.PPSaves / home_goalie_stats.PPShots)
home_goalie_stats.set_index('#', inplace = True)

#way too bulky! future - should be able to do the prep on one table and then filter home vs away
#how can I populate an "N/A" if a field in the json data doesn't exist - no power play opporunities for other team
#game with error - 2021020807





try:
    print(summary_stats)
    print('\nThree Stars of the Game\n')
    print(threeStars)
    input()
    print('\n\nHome Skater Stats\n\n')
    print(home_skater_stats)
    print('\n\nHome Goalie Stats\n')
    print(home_goalie_stats)
    print('\n\nAway Skater Stats\n')
    print(away_skater_stats)
    print('\n\nAway Goalie Stats\n')
    print(away_goalie_stats)
    print('-'*15)
except Exception:
    import traceback
    traceback.print_last()
    raise



