#starting page to ask for you favorite team to store

import pandas as pd
import json
from tables import teams
pd.set_option('display.max_rows', 32) #allow display of all teams

nhl_valid_list = teams['abbreviation'].to_list() #setup list for input validation

def get_nhl_fave():
    print(teams[["name","abbreviation"]].sort_values("name"))
    while True:
        nhl_fave = input("Type abbreviation of your favorite NHL team: ")
        if nhl_fave in nhl_valid_list:
            faveID = teams[teams['abbreviation'] == nhl_fave].index.values.astype(str)[0]
            faveName = teams[teams['abbreviation'] == nhl_fave]['name'].values.astype(str)[0]
            #open and edit _dicts.json to add NHL favorite
            with open('_dicts.json') as f:
                data = json.load(f)
            temp = data["faves"]
            temp["NHL"] = faveID
            with open('_dicts.json', 'w') as f:
                json.dump(data, f)
            print(faveName + ' set as favorite team')
            break
        else:
            print('Sorry, that is not a valid team.')

get_nhl_fave()
