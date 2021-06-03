import pandas as pd

from Functions import time_from_string

def treat_line(action, difference, maxDifference):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - action: action that we are going to study (list)
    - difference: current scoreboard difference (integer)
    - maxPartial: current maximum scoreboard difference for each team (list of integer)
    Output: current scoreboard difference (integer)
    '''
    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team = int(action[1])
            points = int(action[4])
            if team == 1:
                difference += points
                if difference > maxDifference[0]:
                    maxDifference[0] = difference
            else:
                difference -= points
                if -difference > maxDifference[1]:
                    maxDifference[1] = -difference
                
    return difference


def main(file, timestamp=None):
    '''
    This function returns the difference in favour of each team
    - file: play-by-play input file (string)
    - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value (string)
    Output: difference in favour for each team (list of integers)
    '''
    difference = 0
    maxDifference = [0, 0]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        action = line.split(", ")

        if timestamp is not None: # we want the value at the timestamp
            clock = action[0]
            if time_from_string(timestamp) > time_from_string(clock):
                if difference > 0:
                    return [difference, 0]
                return [0, -difference]

        difference = treat_line(action, difference, maxDifference)

    if timestamp is not None: # the timestamp might be after the last play
        if difference > 0:
            return [difference, 0]
        return [0, -difference]
    return maxDifference