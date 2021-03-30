import os
import datetime
import pandas as pd
import numpy as np
import seaborn
import matplotlib.pyplot as plt


def treat_line(line, assists):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - streak: current scoring streak being computed (integer)
    - max_streak: current scoring streak for each team (list of integer)
    - last_team: last team that scored (string)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        dist_given = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + dist_given]
        if result == "I": # the shot was in
            if len(action) == 8+dist_given and action[6+dist_given] == "A": # there is an assist
                team = int(action[1])
                player = action[2]
                assistant = action[7+dist_given]

                # if player not in assists[team-1].columns:
                #     assists[team-1][player] = [0]*len(assists[team-1].index)
                # if assistant not in assists[team-1].index:
                #     row = [0]*len(assists[team-1].columns)
                #     assists[team-1].loc[assistant] = row

                if player not in assists[team-1].columns:
                    assists[team-1][player] = [0]*len(assists[team-1].index)
                    row = [0]*len(assists[team-1].columns)
                    assists[team-1].loc[player] = row
                if assistant not in assists[team-1].columns:
                    assists[team-1][assistant] = [0]*len(assists[team-1].index)
                    row = [0]*len(assists[team-1].columns)
                    assists[team-1].loc[assistant] = row
                assists[team-1].loc[assistant, player] += 1

                # if team == 1:
                #     print(assists[team-1])


def AssistMapMain(file):
    '''
    This function draws the assists between each team members
    - file: play-by-play input file (string)
    '''
    os.chdir(os.path.dirname(__file__))

    assists = [pd.DataFrame(dtype=int), pd.DataFrame(dtype=int)]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            treat_line(line, assists)
    assists[0] = assists[0].astype({assists[0].columns[0]: 'int'})
    assists[1] = assists[1].astype({assists[1].columns[0]: 'int'})

    for i in range(2):
        assists[i].sort_index(0, inplace=True)
        assists[i].sort_index(1, inplace=True)
        # assists[i]["TOTAL"] = assists[0].apply(np.sum, axis=1)
        # assists[i].loc["TOTAL"] = assists[0].apply(np.sum)

    print(seaborn.heatmap(assists[0]))
    plt.imshow(assists[0])
    plt.show()

    return assists