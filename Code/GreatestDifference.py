import pandas as pd


def treat_line(line, difference, maxDifference):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - difference: current scoreboard difference (integer)
    - maxPartial: current maximum scoreboard difference for each team (list of integer)
    Output: current scoreboard difference (integer)
    '''
    action = line.split(", ")

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


def main(file):
    '''
    This function returns the greatest difference in favour of each team
    - file: play-by-play input file (string)
    Output: maximum difference in favour for each team (list of integers)
    '''
    difference = 0
    maxDifference = [0, 0]

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            difference = treat_line(line, difference, maxDifference)

    return maxDifference