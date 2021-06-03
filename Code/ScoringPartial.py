import pandas as pd

from Functions import time_from_string

def treat_line(action, partial, maxPartial, lastTeam):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - action: action that we are going to study (list)
    - partial: current scoring partial being computed (integer)
    - maxPartial: current scoring partial for each team (list of integer)
    - lastTeam: last team that scored (string)
    Output:
    - lastTeam: last team that scored (integer)
    - partial: current partial scoring for lastTeam (integer)
    '''
    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team = int(action[1])
            points = int(action[4])
            if team == lastTeam:
                partial += points
                if partial > maxPartial[lastTeam-1]:
                    maxPartial[lastTeam-1] = partial
            else:
                lastTeam = team
                partial = points

    return lastTeam, partial


def main(file, timestamp=None):
    '''
    This function returns the number of consecutive points for each team without the other one scoring
    - file: play-by-play input file (string)
    - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value (string)
    Output: partial in favour for each team (list of integers)
    '''
    partial = 0
    maxPartial = [0, 0]
    lastTeam = 0

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        action = line.split(", ")

        if timestamp is not None: # we want the value at the timestamp
            clock = action[0]
            if time_from_string(timestamp) > time_from_string(clock):
                if lastTeam == 1:
                    return [partial, 0]
                return [0, partial]

        lastTeam, partial = treat_line(action, partial, maxPartial, lastTeam)

    if timestamp is not None: # the timestamp might be after the last play
        if lastTeam == 1:
            return [partial, 0]
        return [0, partial]

    return maxPartial