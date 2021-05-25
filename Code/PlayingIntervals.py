import datetime

from Functions import *


def add_interval(intervals, interval, five):
    '''
    This functions links a five to an interval adding it to the intervals list
    - intervals: intervals of playing fives (dictionary of {tuple: set})
    - interval: interval of the game without changes (tuple: (string, string))
    - five: set of players (set)
    '''
    intervals[interval] = five


def check_oncourt(team, player, Q, oncourt, tempOncourtIntervals, oncourtIntervals):
    '''
    This function is launched to check whether the presence of the player was already detected. In
    case it was not, it adds it to the players on court and to the previous fives if needed
    - team: team of the player, either 1 or 2 (string)
    - player: name of the player (string)
    - Q: current quarter (string)
    - oncourt: players on court (list of dictionaries {player: string})
    - tempOncourtIntervals: players on court for each interval without changes waiting to be completed (dictionary of {tuple: set of strings})
    - oncourtIntervals: players on court for each interval without changes (dictionary of {tuple: set of strings})
    '''
    if player != "-":
        # we check the player is in the current playing list:
        if player not in oncourt[team-1]:
            clock = quarter_start_time(Q)
            oncourt[team-1][player] = string_from_time(clock)
        # we add the player to previous incomplete fives:
        if len(tempOncourtIntervals[team-1]) > 0:
            toDelete = []
            for interval in tempOncourtIntervals[team-1]:
                tempOncourtIntervals[team-1][interval].add(player)
                # if any five is now complete we add it to the definitive dictionary and delete them from the temporal one:
                if len(tempOncourtIntervals[team-1][interval]) == 5:
                    add_interval(oncourtIntervals[team-1], interval, tempOncourtIntervals[team-1][interval])
                    toDelete.append(interval)
            for interval in toDelete:
                del tempOncourtIntervals[team-1][interval]


def quarter_end(Q, oncourt, playerIntervals, oncourtIntervals, lastChange):
    '''
    This function is launched every time a quarter end is detected.
    It treats the quarter end as a change, as the five players can be completely new at the next quarter
    - Q: quarter that has just ended (string)
    - oncourt: players on court at the time of the action (list of dictionaries {player: string})
    - playersIntervals: playing intervals for every team member (dictionary of {string: list of tuples})
    - oncourtIntervals: players on court for each interval without changes (dictionary of {tuple: set of strings})
    - lastChange: time of the last change (string)
    '''
    # we add the minutes of the players that end the quarter (as it is usually done when they are changed):
    clock = quarter_end_time(Q)
    clock = string_from_time(clock)
    for team in range(1,3):
        for player in oncourt[team-1]:
            if player not in playerIntervals[team-1].keys():
                playerIntervals[team-1][player] = []
            playerIntervals[team-1][player].append((oncourt[team-1][player], clock))
        add_interval(oncourtIntervals[team-1], (lastChange[team-1], clock), set(oncourt[team-1]))

        # we delete current variables as the five players can be completely new at the next quarter:
        oncourt[team-1].clear()
        lastChange[team-1] = string_from_time(quarter_start_time(next_quarter(Q)))


def quarter_check(action, prevQ, oncourt, playerIntervals, oncourtIntervals, lastChange):
    '''
    This function is launched to detect a change of quarter. If it is the case, quarter_end is launched
    - action: play that we are going to study (list)
    - prevQ: quarter of the previous action (string)
    - oncourt: players on court at the time of the action (list of dictionaries {player: string})
    - playersIntervals: playing intervals for every team member (dictionary of {string: list of tuples})
    - tempOncourtIntervals: players on court for each interval without changes waiting to be completed (dictionary of {tuple: set of strings})
    - oncourtIntervals: players on court for each interval without changes (dictionary of {tuple: set of strings})
    - lastChange: time of the last change (string)
    Output: quarter of the action (string)
    '''
    clock = action[0]
    Q = quarter_from_time(clock)
    if prevQ != Q:
        quarter_end(prevQ, oncourt, playerIntervals, oncourtIntervals, lastChange)
    return Q


def change(action, Q, oncourt, playerIntervals, tempOncourtIntervals, oncourtIntervals, lastChange):
    '''
    Treatment of an action that was detected as a change. It will have the following structure:
        clock team player playerOut playerIn
    The change will mean the end of a five and the start of another one
    - action: studied play (list)
    - Q: quarter of the action (string)
    - oncourt: players on court at the time of the action (list of dictionaries {player: string})
    - playersIntervals: playing intervals for every team member (dictionary of {string: list of tuples})
    - tempOncourtIntervals: players on court for each interval without changes waiting to be completed (dictionary of {tuple: set of strings})
    - oncourtIntervals: players on court for each interval without changes (dictionary of {tuple: set of strings})
    - lastChange: time of the last change (string)
    '''
    clock, team, playerOut, playerIn = action[0], int(action[1]), action[2], action[4]
    check_oncourt(team, playerOut, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
    Q, minutes, seconds = clock.split(":")
    clock = Q + ":" + datetime.time(0, int(minutes), int(seconds)).strftime("%M:%S")

    # playerIntervals treatment: player played from oncourt[team-1][playerOut] until clock
    if playerOut not in playerIntervals[team-1].keys():
        playerIntervals[team-1][playerOut] = []
    playerIntervals[team-1][playerOut].append((oncourt[team-1][playerOut], clock))

    if clock != lastChange[team-1]: # to avoid adding fives in the middle of consecutive changes
        if len(oncourt[team-1]) == 5: # if the five is complete, we send it to the definitive list
            add_interval(oncourtIntervals[team-1], (lastChange[team-1], clock), set(oncourt[team-1]))
        else: # if the five is incomplete, we send it to the temporal list
            add_interval(tempOncourtIntervals[team-1], (lastChange[team-1], clock), set(oncourt[team-1]))
    del oncourt[team-1][playerOut]
    oncourt[team-1][playerIn] = clock
    lastChange[team-1] = clock


def treat_line(line, prevQ, oncourt, playerIntervals, tempOncourtIntervals, oncourtIntervals, lastChange):
    '''
    This function is launched to detect the type of play an action is and treat it in case it is a shot
    - line: action that we are going to study (string)
    - prevQ: quarter of the previous action (string)
    - oncourt: players on court at the time of the action (list of dictionaries {player: string})
    - playersIntervals: playing intervals for every team member (dictionary of {string: list of tuples})
    - tempOncourtIntervals: players on court for each interval without changes waiting to be completed (dictionary of {tuple: set of strings})
    - oncourtIntervals: players on court for each interval without changes (dictionary of {tuple: set of strings})
    - lastChange: time of the last change (string)
    Output: quarter of the action (string)
    '''
    action = line.split(", ")

    Q = quarter_check(action, prevQ, oncourt, playerIntervals, oncourtIntervals, lastChange)
    if len(action) > 3 and action[3] == "S": # there can be either one or two players
        team, player = int(action[1]), action[2]
        check_oncourt(team, player, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        if len(action) == 8+distGiven and action[6+distGiven] == "A": # there is an assist
            assistant = action[7+distGiven]
            check_oncourt(team, assistant, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
    elif len(action) > 3 and (action[3] == "R" or action[3] == "T"): # there is only one player
        team, player = int(action[1]), action[2]
        check_oncourt(team, player, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
    elif len(action) > 3 and (action[3] == "St" or action[3] == "B"): # there are two players
        team, player, receiver = int(action[1]), action[2], action[4]
        check_oncourt(team, player, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
        opTeam = other_team(team)
        check_oncourt(opTeam, receiver, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
    elif len(action) > 3 and action[3] == "F": # there can be either one or two players
        team, player = int(action[1]), action[2]
        check_oncourt(team, player, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
        if len(action) == 6: # there is a player from the opposite team that receives the foul
            receiver = action[5]
            opTeam = other_team(team)
            check_oncourt(opTeam, receiver, Q, oncourt, tempOncourtIntervals, oncourtIntervals)
    elif len(action) > 3 and action[3] == "C":
        change(action, Q, oncourt, playerIntervals, tempOncourtIntervals, oncourtIntervals, lastChange)
    return Q


def main(file):
    '''
    This function returns the playing intervals for every player and the 5 on court for each interval
    - file: play-by-play input file (string)
    Output:
    - playersIntervals: playing intervals for every team member (dictionary of {string: list of tuples})
    - oncourtIntervals: players on court for each interval without changes (dictionary of {tuple: set of strings})
    '''
    playerIntervals = [{}, {}]
    oncourt = [{}, {}]
    tempOncourtIntervals = [{}, {}]
    oncourtIntervals = [{}, {}]
    lastChange = ["1Q:12:00", "1Q:12:00"]
    Q = "1Q"

    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        Q = treat_line(line, Q, oncourt, playerIntervals, tempOncourtIntervals, oncourtIntervals, lastChange)
    quarter_end(Q, oncourt, playerIntervals, oncourtIntervals, lastChange)

    return playerIntervals, oncourtIntervals