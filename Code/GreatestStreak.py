import os
import datetime
import pandas as pd
import numpy as np

from Functions import *


def treat_line(line, streak, max_streak, last_team):
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
            team = int(action[1])
            points = int(action[4])
            if team == last_team:
                streak += points
            else:
                if streak > max_streak[last_team-1]:
                    max_streak[last_team-1] = streak
                last_team = team
                streak = points
            

    return streak, last_team


def GreatestStreakMain(file):
    '''
    This function returns the greatest scoring streak for every team
    - file: play-by-play input file (string)
    '''
    os.chdir(os.path.dirname(__file__))

    streak = 0
    max_streak = [0, 0]
    last_team = 0

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            streak, last_team = treat_line(line, streak, max_streak, last_team)

    return max_streak