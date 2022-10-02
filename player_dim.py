#setup python ETL process to refresh dimensional player data

import sys
import re
import os
import requests as rq
import pandas as pd
import json as json
from json import loads

season_start = 20202021
season_end = 20212022
base = "https://statsapi.web.nhl.com/"
endpoint = "api/v1/schedule/?season="

urls = []
id_array = []

#create list of URLs to pull (need one URL for each season)
x = season_start
s1 = season_start // 10000
s2 = (season_end // 10000)+1
for i in range(s2 - s1):
    urls.append(base + endpoint + str(x))
    x = x + 10001

#use URL list to pull gameIDs from each season and append them to "id_array"
x = 0
for i in range(s2-s1):
    url = urls[x]
    response = rq.get(url)
    games = response.json()
    for i in range(len(games["dates"])):
        for j in range(len(games["dates"][i]["games"])):
            id_array.append(games["dates"][i]["games"][j]["gamePk"])
    x = x + 1  

print(id_array)