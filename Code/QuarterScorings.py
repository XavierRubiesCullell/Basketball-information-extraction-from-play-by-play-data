import pandas as pd
import numpy as np

from Functions import *


def define_index(scores):
    '''
    This function returns the quarter related to the information that is going to be written
    - scores: scoring table (pandas.DataFrame)
    Output: next quarter (string)
    '''
    ncols = len(scores.columns)
    if ncols < 4:
        return str(ncols+1) + "Q"
    else:
        return str(ncols-3) + "OT"


def quarter_check(clock, end, prevQ, scores, QScores):
    '''
    This function is launched to detect a change of quarter
    - clock: time of the play we are treating (datetime.time)
    - end: ending time we are considering (datetime.time)
    - prevQ: quarter of the previous play (integer)
    - scores: scoring table (pandas.dataframe)
    - QScores: temporary quarter scoring (list of integers)
    Ouput: quarter of the play (integer)
    '''
    Q = quarter_index_from_time(clock)
    # If there is a quarter change, we write down the quarter result
    # Without the second restriction, if end is in Q_t and clock in Q_{t+1}, [0, 0] would be written for Q_{t+1} at Main
    if prevQ != Q and clock >= end:
        index = define_index(scores)
        scores[index] = QScores
        QScores[0] = QScores[1] = 0
        prevQ = Q
    return Q


def treat_line(line, scores, QScores, prevQ, end):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - scores: scoring table (dataframe)
    - QScores: temporary quarter scoring (list)
    - prevQ: quarter of the previous play (integer)
    - end: ending time we are considering (datetime.time)
    Ouput:
    - Q: quarter of the play (integer)
    - clock: timestamp of the play (datetime.timedelta)
    '''
    action = line.split(", ")

    clock = action[0]
    clock = time_from_string(clock)
    Q = quarter_check(clock, end, prevQ, scores, QScores)

    if clock >= end and len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team, points = action[1], action[4]
            QScores[int(team)-1] += int(points)

    return Q, clock


def main(file, home, away, end):
    '''
    This function returns the partial scorings scoreboard
    - file: play-by-play input file (string)
    - home: local team (string)
    - away: visiting team (string)
    - end: ending time we are considering (string)
    Output: scoring of the quarters and total scoring (pandas.DataFrame)
    '''
    scores = pd.DataFrame(index=[home, away])
    QScores = [0, 0]
    Q = 1
    end = time_from_string(end)

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            Q, clock = treat_line(line, scores, QScores, Q, end)
            if clock < end:
                break

    index = define_index(scores)
    scores[index] = QScores
    scores["T"] = scores.apply(np.sum, axis=1)
    return scores