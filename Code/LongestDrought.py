import os
import datetime
import pandas as pd
import numpy as np

from Functions import *


def treat_line(line, time, max_time):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - scores: scoring table (dataframe)
    - Q_scores: temporary quarter scoring (list)
    - prev_Q: quarter from the previous play (integer)
    '''
    action = line.split(", ")

    if len(action) > 3 and action[3] == "S":
        dist_given = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + dist_given]
        if result == "I": # the shot was in
            clock = time_from_string(action[0])
            team = int(action[1])
            if time[team-1] is not None:
                diff, _, _ = compute_interval(time[team-1], clock)
                if max_time[team-1] is None or diff > max_time[team-1]:
                    max_time[team-1] = diff
            time[team-1] = clock

    return time, max_time


def LongestDroughtMain(file):
    '''
    This function returns the partial scorings scoreboard
    - file: play-by-play input file (string)
    '''
    os.chdir(os.path.dirname(__file__))

    time = [None, None]
    max_time = [None, None]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        Q = 1
        for line in lines:
            line = line.strip()
            time, max_time = treat_line(line, time, max_time)
        
        for team in range(1,3):
            diff, _, _ = compute_interval(time[team-1], time_from_string("00:00"))
            if diff > max_time[team-1]:
                max_time[team-1] = diff
    return tuple(map(str, max_time))