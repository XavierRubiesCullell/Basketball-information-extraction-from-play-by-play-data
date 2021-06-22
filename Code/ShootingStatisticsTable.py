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
        if action[4] != "1" and distGiven:
            team, points, dist, result = int(action[1]), action[4], action[5], action[6]

            if dist + " " + points not in shots[team-1].index:
                newRow = [int(dist), int(points), 0, 0]
                newRow = pd.Series(newRow, index=['Distance (ft)', 'Points', 'Shots made', 'Shots attempted'], name = dist + " " + points)
                shots[team-1] = shots[team-1].append(newRow)
            
            shots[team-1].loc[dist + " " + points, 'Shots attempted'] += 1
            if result == "I": # the shot was in
                shots[team-1].loc[dist + " " + points, 'Shots made'] += 1
            

def main(file, shots=None):
    '''
    This function builds the shooting statistics table
    - file: play-by-play input file (string)
    - shots: if not null, matrix where the shooting values will be added (pandas.DataFrame)
    Output: shooting table (pandas.DataFrame)
    '''
    if shots is None:
        shots = [ pd.DataFrame(columns=['Distance (ft)', 'Points', 'Shots made', 'Shots attempted', 'Accuracy (%)', 'ExpPts']) ]*2
        temp = False
    else:
        shots[0] = shots[0].drop(index = ["TOTAL"], errors='ignore')
        shots[1] = shots[1].drop(index = ["TOTAL"], errors='ignore')
        temp = True

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        treat_line(line, shots)
    if not temp: # the table is not a temporal value
        for team in range(1,3):
            shots[team-1] = shots[team-1].sort_values(by=['Distance (ft)', 'Points'], ascending=True, ignore_index=True)
            shots[team-1].loc["TOTAL"] = shots[team-1].apply(sum)
            shots[team-1]['Accuracy (%)'] = round(shots[team-1]['Shots made']/shots[team-1]['Shots attempted']*100, 2)
            shots[team-1]['ExpPts'] = [x*y/100 for x,y in zip(shots[team-1]['Accuracy (%)'], shots[team-1]['Points'])]
            # arrangements for table visualisation:
            shots[team-1] = shots[team-1].round({'ExpPts': 2})
            shots[team-1] = shots[team-1].astype({'Distance (ft)': 'int32', 'Points': 'int32', 'Shots made': 'int32', 'Shots attempted': 'int32'})
            shots[team-1].loc["TOTAL", 'Distance (ft)'] = shots[team-1].loc["TOTAL", 'Points'] = shots[team-1].loc["TOTAL", 'ExpPts'] = "-"
    return shots