import pandas as pd

from Functions import time_from_string, other_team

def treat_line(action, streak, maxStreak):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - action: action that we are going to study (list)
    - streak: current scoring streak (list of integers)
    - maxStreak: current maximum scoring streak (list of integers)
    '''
    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is neither I nor O, so in this position we have the distance
        result = action[5 + distGiven]
        team = int(action[1])
        if result == "I": # the shot was in, we increment the streak
            points = int(action[4])
            streak[team-1] += points
            if streak[team-1] > maxStreak[team-1]:
                maxStreak[team-1] = streak[team-1]
        else: # the shot was out, we stop the streak computation and update the maximum value in case it is higher
            streak[team-1] = 0

    elif len(action) > 3 and action[3] == "B": # a block by team 1 is a missed shot by team 2
        team = int(action[1])
        opTeam = other_team(team)
        streak[opTeam-1] = 0
                

def main(file, timestamp=None):
    '''
    This function returns the amount of consecutive points without missing for every team
    - file: play-by-play input file (string)
    - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value (string)
    Output: scoring streak for each team (list of integers)
    '''
    streak = [0, 0]
    maxStreak = [0, 0]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        action = line.split(", ")

        if timestamp is not None: # we want the value at the timestamp
            clock = action[0]
            if time_from_string(timestamp) > time_from_string(clock):
                return streak

        treat_line(action, streak, maxStreak)

    if timestamp is not None: # the timestamp might be after the last play
        return streak
    return maxStreak