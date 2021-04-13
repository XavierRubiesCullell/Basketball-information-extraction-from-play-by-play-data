import os
import datetime
import pandas as pd
import numpy as np

from Functions import *


def add_interval(intervals, interval, five):
    '''
    This functions links a five to an interval adding it to the intervals list
    Input:
    - intervals: intervals of playing fives (dictionary of tuple: set)
    - interval: interval of the game without changes (tuple: (string, string))
    - five: set of players (set)
    '''
    intervals[interval] = five


def check_oncourt(team, player, Q, oncourt, temponcourtintervals, oncourtintervals):
    '''
    This function is launched to check whether the presence of the player was already detected. In
    case it was not, it adds it to the players on court and to the previous fives if needed
    Input:
    - team: team of the player, either 1 or 2 (string)
    - player: name of the player (string)
    - Q: current quarter (integer)
    - oncourt: players on court (list of dictionaries player: string)
    - temponcourtintervals: players on court for each interval without changes waiting to be completed (dictionary of tuple: set of strings)
    - oncourtintervals: players on court for each interval without changes (dictionary of tuple: set of strings)
    '''
    if player != "-":
        # we check the player is in the current playing list:
        if player not in oncourt[team-1]:
            clock = datetime.time(0, (5-Q)*12, 0)
            oncourt[team-1][player] = string_from_time(clock)
        # we add the player to previous incomplete fives:
        if len(temponcourtintervals[team-1]) > 0:
            todelete = []
            for interval in temponcourtintervals[team-1]:
                temponcourtintervals[team-1][interval].add(player)
                # if any five is now complete we add it to the definitive dictionary and delete them from the temporal one:
                if len(temponcourtintervals[team-1][interval]) == 5:
                    add_interval(oncourtintervals[team-1], interval, temponcourtintervals[team-1][interval])
                    todelete.append(interval)
            for interval in todelete:
                del temponcourtintervals[team-1][interval]


def quarter_end(Q, oncourt, playerintervals, oncourtintervals, lastchange):
    '''
    This function is launched every time a quarter end is detected.
    It treats the quarter end as a change, as the five players can be completely new at the next quarter
    Input:
    - Q: quarter that has just ended (integer)
    - oncourt: players on court at the time of the action (list of dictionaries player: string)
    - playersintervals: playing intervals for every team member (dictionary of string: list of tuples)
    - oncourtintervals: players on court for each interval without changes (dictionary of tuple: set of strings)
    - lastchange: time of the last change (string)
    '''
    # we add the minutes of the players that end the quarter (as it is usually done when they are changed):
    clock = datetime.time(0, 12*(4-Q), 0)
    clock = string_from_time(clock)
    for team in range(1,3):
        for player in oncourt[team-1]:
            if player not in playerintervals[team-1].keys():
                playerintervals[team-1][player] = []
            playerintervals[team-1][player].append((oncourt[team-1][player], clock))
        add_interval(oncourtintervals[team-1], (lastchange[team-1], clock), set(oncourt[team-1]))

        # we delete current variables as the five players can be completely new at the next quarter:
        oncourt[team-1].clear()
        lastchange[team-1] = clock


def quarter_check(action, prev_Q, oncourt, playerintervals, oncourtintervals, lastchange):
    '''
    This function is launched to detect a change of quarter. If it is the case, quarter_end is launched
    Input:
    - action: play that we are going to study (list)
    - prev_Q: quarter of the previous action (integer)
    - oncourt: players on court at the time of the action (list of dictionaries player: string)
    - playersintervals: playing intervals for every team member (dictionary of string: list of tuples)
    - temponcourtintervals: players on court for each interval without changes waiting to be completed (dictionary of tuple: set of strings)
    - oncourtintervals: players on court for each interval without changes (dictionary of tuple: set of strings)
    - lastchange: time of the last change (string)
    '''
    clock = action[0]
    clock = time_from_string(clock)
    Q = (4-int(clock.minute/12))
    if prev_Q != Q:
        quarter_end(prev_Q, oncourt, playerintervals, oncourtintervals, lastchange)
    return Q


def change(action, Q, oncourt, playerintervals, temponcourtintervals, oncourtintervals, lastchange):
    '''
    Treatment of an action that was detected as a change. It will have the following structure:
        clock team player playerOut playerIn
    The change will mean the end of a five and the start of another one
    Input:
    - action: studied play (list)
    - Q: quarter of the action (integer)
    - oncourt: players on court at the time of the action (list of dictionaries player: string)
    - playersintervals: playing intervals for every team member (dictionary of string: list of tuples)
    - temponcourtintervals: players on court for each interval without changes waiting to be completed (dictionary of tuple: set of strings)
    - oncourtintervals: players on court for each interval without changes (dictionary of tuple: set of strings)
    - lastchange: time of the last change (string)
    '''
    clock, team, playerOut, playerIn = action[0], int(action[1]), action[2], action[4]
    check_oncourt(team, playerOut, Q, oncourt, temponcourtintervals, oncourtintervals)

    # playerintervals treatment: player played from oncourt[team-1][playerOut] until clock
    if playerOut not in playerintervals[team-1].keys():
        playerintervals[team-1][playerOut] = []
    playerintervals[team-1][playerOut].append((oncourt[team-1][playerOut], clock))

    if clock != lastchange[team-1]: # to avoid adding fives in the middle of consecutive changes
        if len(oncourt[team-1]) == 5: # if the five is complete, we send it to the definitive list
            add_interval(oncourtintervals[team-1], (lastchange[team-1], clock), set(oncourt[team-1]))
        else: # if the five is incomplete, we send it to the temporal list
            add_interval(temponcourtintervals[team-1], (lastchange[team-1], clock), set(oncourt[team-1]))
    del oncourt[team-1][playerOut]
    oncourt[team-1][playerIn] = clock
    lastchange[team-1] = clock


def treat_line(line, prev_Q, oncourt, playerintervals, temponcourtintervals, oncourtintervals, lastchange):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    Input:
    - line: action that we are going to study (string)
    - prev_Q: quarter of the previous action (integer)
    - oncourt: players on court at the time of the action (list of dictionaries player: string)
    - playersintervals: playing intervals for every team member (dictionary of string: list of tuples)
    - temponcourtintervals: players on court for each interval without changes waiting to be completed (dictionary of tuple: set of strings)
    - oncourtintervals: players on court for each interval without changes (dictionary of tuple: set of strings)
    - lastchange: time of the last change (string)
    '''
    action = line.split(", ")

    Q = quarter_check(action, prev_Q, oncourt, playerintervals, oncourtintervals, lastchange)

    if len(action) > 3 and action[3] == "S": # there can be either one or two players
        team, player = int(action[1]), action[2]
        check_oncourt(team, player, Q, oncourt, temponcourtintervals, oncourtintervals)
        dist_given = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        if len(action) == 8+dist_given and action[6+dist_given] == "A": # there is an assist
            assistant = action[7+dist_given]
            check_oncourt(team, assistant, Q, oncourt, temponcourtintervals, oncourtintervals)
    elif len(action) > 3 and (action[3] == "R" or action[3] == "T"): # there is only one player
        team, player = int(action[1]), action[2]
        check_oncourt(team, player, Q, oncourt, temponcourtintervals, oncourtintervals)
    elif len(action) > 3 and (action[3] == "St" or action[3] == "B"): # there are two players
        team, player, receiver = int(action[1]), action[2], action[4]
        check_oncourt(team, player, Q, oncourt, temponcourtintervals, oncourtintervals)
        op_team = other_team(team)
        check_oncourt(op_team, receiver, Q, oncourt, temponcourtintervals, oncourtintervals)
    elif len(action) > 3 and action[3] == "F": # there can be either one or two players
        team, player = int(action[1]), action[2]
        check_oncourt(team, player, Q, oncourt, temponcourtintervals, oncourtintervals)
        if len(action) == 6: # there is a player from the opposite team that receives the foul
            receiver = action[5]
            op_team = other_team(team)
            check_oncourt(op_team, receiver, Q, oncourt, temponcourtintervals, oncourtintervals)
    elif len(action) > 3 and action[3] == "C":
        change(action, Q, oncourt, playerintervals, temponcourtintervals, oncourtintervals, lastchange)
    
    return Q


def main(file):
    '''
    This function returns the playing intervals for every player and the 5 on court for each interval
    Input:
    - file: play-by-play input file (string)
    Output:
    - playersintervals: playing intervals for every team member (dictionary of string: list of tuples)
    - oncourtintervals: players on court for each interval without changes (dictionary of tuple: set of strings)
    '''
    os.chdir(os.path.dirname(__file__))

    playerintervals = [{}, {}]
    oncourt = [{}, {}]
    temponcourtintervals = [{}, {}]
    oncourtintervals = [{}, {}]
    lastchange = ["48:00", "48:00"]
    Q = 1

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            Q = treat_line(line, Q, oncourt, playerintervals, temponcourtintervals, oncourtintervals, lastchange)
    quarter_end(4, oncourt, playerintervals, oncourtintervals, lastchange)

    return playerintervals, oncourtintervals