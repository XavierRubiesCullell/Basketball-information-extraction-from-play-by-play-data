import pandas as pd
import numpy as np

def treat_line(line, shots):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - shots: table of the shots (pandas.DataFrame)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        if action[4] != "1" and distGiven: # we select only field goals from more than 0 ft
            team, dist, result = int(action[1]), int(action[5]), action[6]

            if dist not in shots[team-1].index:
                newRow = [0]*2
                newRow = pd.Series(newRow, index=['Shots made', 'Shots attempted'], name=dist)
                shots[team-1] = shots[team-1].append(newRow)
            
            shots[team-1].loc[dist, 'Shots attempted'] += 1
            if result == "I": # the shot was in
                shots[team-1].loc[dist, 'Shots made'] += 1
            

def main(file, shots=None):
    '''
    This function builds the shooting statistics table
    - file: play-by-play input file (string)
    - shots: if not null, matrix where the shooting values will be added (pandas.DataFrame)
    Output: shooting table (pandas.DataFrame)
    '''
    if shots is None:
        shots = [ pd.DataFrame(columns=['Shots made', 'Shots attempted', 'Accuracy (%)']) ]*2
        shots[0].index.name = 'Distance (ft)'
        shots[1].index.name = 'Distance (ft)'
    else:
        shots[0] = shots[0].drop(index = ["TOTAL"])
        shots[1] = shots[1].drop(index = ["TOTAL"])

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        treat_line(line, shots)
    
    for team in range(1,3):
        shots[team-1].sort_index(inplace=True)
        shots[team-1].loc["TOTAL"] = shots[team-1].apply(np.sum)
        shots[team-1]['Accuracy (%)'] = round(shots[team-1]['Shots made']/shots[team-1]['Shots attempted']*100, 2)
    
    return shots