import os
import datetime
import pandas as pd
import numpy as np


def treat_line(line, streak, maxStreak, lastTeam):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - streak: current scoring streak being computed (integer)
    - maxStreak: current scoring streak for each team (list of integer)
    - lastTeam: last team that scored (string)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team = int(action[1])
            points = int(action[4])
            if team == lastTeam:
                streak += points
            else:
                if streak > maxStreak[lastTeam-1]:
                    maxStreak[lastTeam-1] = streak
                lastTeam = team
                streak = points

    return streak, lastTeam


def main(file):
    '''
    This function returns the greatest scoring streak for every team
    - file: play-by-play input file (string)
    '''
    os.chdir(os.path.dirname(__file__))

    streak = 0
    maxStreak = [0, 0]
    lastTeam = 0

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            streak, lastTeam = treat_line(line, streak, maxStreak, lastTeam)

    return maxStreak