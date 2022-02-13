#setup recurring data tables with no dynamic gameID requirements

import requests as rq
import pandas as pd

###conference table
response = rq.get("https://statsapi.web.nhl.com/api/v1/conferences")
conferences = pd.json_normalize(response.json()["conferences"]).set_index("id")
conferences.rename_axis("conferenceID", inplace = True)

###division table
response = rq.get("https://statsapi.web.nhl.com/api/v1/divisions")
divisions = pd.json_normalize(response.json()["divisions"]).set_index("id")
divisions.rename_axis("divisionID", inplace = True)

###team table
response = rq.get("https://statsapi.web.nhl.com/api/v1/teams")
teams = pd.json_normalize(response.json()["teams"]).set_index("id")
teams.rename_axis("teamID", inplace = True)

###team standings
response = rq.get("https://statsapi.web.nhl.com/api/v1/standings")
team_standings = pd.json_normalize(response.json()['records'], record_path = ['teamRecords'], errors = 'ignore').set_index("team.id")
team_standings.rename_axis("teamID", inplace = True)

###last played game by teamID
response = rq.get("https://statsapi.web.nhl.com/api/v1/teams?expand=team.schedule.previous")
last = pd.json_normalize(response.json()['teams'], record_path = ['previousGameSchedule', 'dates', 'games'])
home_key = last[['teams.home.team.id', 'gamePk']].rename(columns = {"teams.home.team.id": "teamID", "gamePk": "gameID"})
away_key = last[['teams.away.team.id', 'gamePk']].rename(columns = {"teams.away.team.id": "teamID", "gamePk": "gameID"})
last_game = pd.concat([home_key, away_key]).sort_values('gameID', ascending = False).drop_duplicates(subset = ["teamID"], keep = "first").set_index("teamID")
last_game_dict = last_game.to_dict() #setup last game table as a dictionary
