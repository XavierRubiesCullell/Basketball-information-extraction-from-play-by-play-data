import os
import datetime
import pandas as pd
import numpy as np

def time_from_string(clock):
    '''
    This function returns a datetime type value from a time represented as a string
    - clock: time represented in MM:SS format (string)
    '''
    clock = clock.split(":")
    return datetime.time(0, int(clock[0]), int(clock[1]))


def quarter_check(action, prev_Q, scores, Q_scores):
    clock = action[0]
    clock = time_from_string(clock)
    Q = (4-int(clock.minute/12))
    if prev_Q != Q:
        scores.loc["Home", "Q"+str(prev_Q)] = Q_scores[0]
        scores.loc["Away", "Q"+str(prev_Q)] = Q_scores[1]
        Q_scores[0] = 0
        Q_scores[1] = 0
    return Q


def treat_line(line, scores, Q_scores, prev_Q):
    action = line.split(", ")
    Q = quarter_check(action, prev_Q, scores, Q_scores)

    if len(action) > 3 and action[3] == "S":
        dist_given = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + dist_given]
        if result == "I": # the shot was in
            team, points = action[1], action[4]
            Q_scores[int(team)-1] += int(points)

    return Q


def PartialScoringsMain(file):
    os.chdir(os.path.dirname(__file__))

    scores = pd.DataFrame(index=["Home", "Away"], columns=["Q1", "Q2", "Q3", "Q4"])
    Q_scores = [0, 0]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        Q = 1
        for line in lines:
            line = line.strip()
            Q = treat_line(line, scores, Q_scores, Q)
    scores.loc["Home", "Q4"] = Q_scores[0]
    scores.loc["Away", "Q4"] = Q_scores[1]
    scores["T"] = scores.apply(np.sum, axis=1)
    return scores