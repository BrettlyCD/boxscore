#dynamic responses for specific game data

import requests as rq
import pandas as pd
import json
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

try:
    print(threeStars)
    input()
    print(summary_stats)
except Exception:
    import traceback
    traceback.print_last()
    raise


