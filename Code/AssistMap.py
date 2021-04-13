import os
import datetime
import pandas as pd
import numpy as np
import seaborn
import matplotlib.pyplot as plt


def check_player(player, ast):
    '''
    This function makes sure a player is in the team's assist matrix
    - player: player that is verified. In case it is not already present, it is added. (string)
    - ast: player's team assist matrix (pandas.dataframe)
    '''
    if player not in ast.columns:
        ast[player] = [0]*len(ast.index)
        row = [0]*len(ast.columns)
        ast.loc[player] = row


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
                scorer = action[2]
                assistant = action[7+dist_given]

                check_player(scorer, assists[team-1])
                check_player(assistant, assists[team-1])
                assists[team-1].loc[assistant, scorer] += 1


def main(file):
    '''
    This function draws the assists between each team members
    ast[i][j] indicates the number of assists from player i to player j
    - file: play-by-play input file (string)
    '''
    os.chdir(os.path.dirname(__file__))

    assists = [pd.DataFrame(dtype=int), pd.DataFrame(dtype=int)]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            treat_line(line, assists)

    for i in range(2):
        # correction of automatic .0 at 1st column:
        assists[i] = assists[i].astype({assists[i].columns[0]: 'int'})
        # sorting according to players' name:
        assists[i].sort_index(0, inplace=True)
        assists[i].sort_index(1, inplace=True)
        # marginal values computation:
        assists[i]["TOTAL"] = assists[i].apply(np.sum, axis=1)
        assists[i].loc["TOTAL"] = assists[i].apply(np.sum)

    # print(seaborn.heatmap(assists[0]))
    # plt.imshow(assists[0])
    # plt.show()

    return assists