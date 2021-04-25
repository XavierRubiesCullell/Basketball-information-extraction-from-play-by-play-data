import os
import datetime
import pandas as pd
import numpy as np


def treat_line(line, partial, maxPartial, lastTeam):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - partial: current scoring partial being computed (integer)
    - maxPartial: current scoring partial for each team (list of integer)
    - lastTeam: last team that scored (string)
    Output:
    - lastTeam: last team that scored (integer)
    - partial: current partial scoring for lastTeam (integer)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team = int(action[1])
            points = int(action[4])
            if team == lastTeam:
                partial += points
            else:
                if partial > maxPartial[lastTeam-1]:
                    maxPartial[lastTeam-1] = partial
                lastTeam = team
                partial = points

    return lastTeam, partial


def main(file):
    '''
    This function returns the greatest scoring streak for every team without the other one scoring
    - file: play-by-play input file (string)
    Output: maximum partial in favour for each team (list of integers)
    '''
    os.chdir(os.path.dirname(__file__))

    partial = 0
    maxPartial = [0, 0]
    lastTeam = 0

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            lastTeam, partial = treat_line(line, partial, maxPartial, lastTeam)

    return maxPartial