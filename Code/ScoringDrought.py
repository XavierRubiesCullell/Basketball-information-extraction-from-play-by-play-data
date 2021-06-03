import pandas as pd

from Functions import time_from_string, compute_interval


def treat_line(action, lastTime, maxLength):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - action: action that we are going to study (list)
    - lastTime: last time each team scored (list of datetime.time)
    - maxLength: temporary maximum interval length without scoring for each team (list of datetime.timedelta)
    '''
    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            clock = time_from_string(action[0])
            team = int(action[1])
            diff, _, _ = compute_interval(lastTime[team-1], clock)
            if maxLength[team-1] is None or diff > maxLength[team-1]:
                maxLength[team-1] = diff
            lastTime[team-1] = clock


def main(file, lastQ, timestamp=None):
    '''
    This function returns the time without for every team
    - file: play-by-play input file (string)
    - lastQ: last quarter of the match (string)
    - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value (string)
    Output: time interval without scoring (list)
    '''
    lastTime = [time_from_string("1Q:12:00"), time_from_string("1Q:12:00")]
    maxLength = [None, None]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        action = line.split(", ")

        if timestamp is not None: # we want the value at the timestamp
            clock = action[0]
            if time_from_string(timestamp) > time_from_string(clock):
                diff1, _, _ = compute_interval(lastTime[0], time_from_string(timestamp))
                diff2, _, _ = compute_interval(lastTime[1], time_from_string(timestamp))
                return [str(diff1), str(diff2)]

        treat_line(action, lastTime, maxLength)
    
    if timestamp is not None: # the timestamp might be after the last play
        diff1, _, _ = compute_interval(lastTime[0], time_from_string(f"{lastQ}:00:00"))
        diff2, _, _ = compute_interval(lastTime[1], time_from_string(f"{lastQ}:00:00"))
        return [str(diff1), str(diff2)]

    # we must check the end of the match:
    for team in range(1,3):
        diff, _, _ = compute_interval(lastTime[team-1], time_from_string(f"{lastQ}:00:00"))
        if diff > maxLength[team-1]:
            maxLength[team-1] = diff
    return tuple(map(str, maxLength))