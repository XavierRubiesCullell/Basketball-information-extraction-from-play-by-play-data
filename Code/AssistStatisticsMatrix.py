import pandas as pd
import numpy as np


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
    - assists: matrix of the assists (pandas.DataFrame)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            if len(action) == 8+distGiven and action[6+distGiven] == "A": # there is an assist
                team = int(action[1])
                scorer = action[2]
                assistant = action[7+distGiven]

                check_player(scorer, assists[team-1])
                check_player(assistant, assists[team-1])
                assists[team-1].loc[assistant, scorer] += 1


def main(file, assists=None):
    '''
    This function draws the assists between each team members
    assists[i][j] indicates the number of assists from player i to player j
    - file: play-by-play input file (string)
    - assists: if not null, matrix where the assist values will be added (pandas.DataFrame)
    Output: assist matrix (pandas.DataFrame)
    '''
    if assists is None:
        assists = [pd.DataFrame(dtype=int), pd.DataFrame(dtype=int)]
    else:
        assists[0] = assists[0].drop(index = ["TOTAL"], errors='ignore')
        assists[0] = assists[0].drop(columns = ["TOTAL"], errors='ignore')
        assists[1] = assists[1].drop(index = ["TOTAL"], errors='ignore')
        assists[1] = assists[1].drop(columns = ["TOTAL"], errors='ignore')

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        treat_line(line, assists)

    for team in range(1,3):
        # correction of automatic .0 at 1st column:
        assists[team-1] = assists[team-1].astype({assists[team-1].columns[0]: 'int'})
        # sorting according to players' name:
        assists[team-1].sort_index(0, inplace=True)
        assists[team-1].sort_index(1, inplace=True)
        # marginal values computation:
        assists[team-1]["TOTAL"] = assists[team-1].apply(np.sum, axis=1)
        assists[team-1].loc["TOTAL"] = assists[team-1].apply(np.sum)

    return assists