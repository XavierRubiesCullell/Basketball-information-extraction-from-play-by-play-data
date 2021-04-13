import os
import datetime
import pandas as pd
import numpy as np

from Functions import *


def treat_line(line, lastTime, maxLength):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - lastTime: last time each team scored (list of datetime.time)
    - maxLength: temporary maximum interval length without scoring for each team (list of datetime.timedelta)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            clock = time_from_string(action[0])
            team = int(action[1])
            if lastTime[team-1] is not None:
                diff, _, _ = compute_interval(lastTime[team-1], clock)
                if maxLength[team-1] is None or diff > maxLength[team-1]:
                    maxLength[team-1] = diff
            lastTime[team-1] = clock


def main(file):
    '''
    This function returns the longest time for every team without scoring
    - file: play-by-play input file (string)
    '''
    os.chdir(os.path.dirname(__file__))

    lastTime = [None, None]
    maxLength = [None, None]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            treat_line(line, lastTime, maxLength)
        
        for team in range(1,3):
            diff, _, _ = compute_interval(lastTime[team-1], time_from_string("00:00"))
            if diff > maxLength[team-1]:
                maxLength[team-1] = diff
    return tuple(map(str, maxLength))