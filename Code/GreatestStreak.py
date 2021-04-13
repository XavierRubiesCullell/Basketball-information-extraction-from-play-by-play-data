import os
import datetime
import pandas as pd
import numpy as np

from Functions import *


def treat_line(line, streak, maxStreak):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - streak: current scoring streak (list of integers)
    - maxStreak: current maximum scoring streak (list of integers)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        team = int(action[1])
        distGiven = action[5] != "I" and action[5] != "O" # true if it is neither I nor O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in, we increment the streak
            points = int(action[4])
            streak[team-1] += points
        else: # the shot was out, we stop the streak computation and update the maximum value in case it is higher
            if streak[team-1] > maxStreak[team-1]:
                maxStreak[team-1] = streak[team-1]
            streak[team-1] = 0

    elif len(action) > 3 and action[3] == "B": # a block by team 1 is a missed shot by team 2
        team = int(action[1])
        opTeam = other_team(team)
        if streak[opTeam-1] > maxStreak[opTeam-1]:
            maxStreak[opTeam-1] = streak[opTeam-1]
        streak[opTeam-1] = 0
                

def main(file):
    '''
    This function returns the maximum amount of consecutive points without missing for every team
    - file: play-by-play input file (string)
    '''
    os.chdir(os.path.dirname(__file__))

    streak = [0, 0]
    maxStreak = [0, 0]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            treat_line(line, streak, maxStreak)

    for team in range(1,3):
        if streak[team-1] > maxStreak[team-1]:
            maxStreak[team-1] = streak[team-1]

    return maxStreak