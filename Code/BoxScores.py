import pandas as pd
import datetime
import os
import numpy as np

from Functions import *

def modify_table(table, team, player, variable, value):
    '''
    This function is launched to modify the boxscore values
    '''
    table[team-1].loc[player,variable] += value


def check_player(table, team, player):
    '''
    This function is launched to avoid an error due to a missing key (player) in a boxscore table
    - team: team of the player, either 1 or 2 (string)
    - player: name of the player (string)
    '''
    if player not in table[team-1].index:
        newrow = [datetime.timedelta()] + [0]*(len(categories)-1)
        newrow = pd.Series(newrow, index=categories, name=player)
        table[team-1] = table[team-1].append(newrow)


def check_oncourt(oncourt, team, player, clock, start, end, table, plusminus):
    '''
    This function is launched to check whether the presence of the player was already detected.
    In case it was not, it adds it to the players on court and adds the player +/- missing
    - team: team of the player, either 1 or 2 (string)
    - player: name of the player (string)
    - clock: time of a specific moment (string)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    Q = get_quarter(clock)
    if player != "-" and player not in oncourt[team-1]:
        oncourt[team-1][player] = datetime.time(0, (5-Q)*12, 0)
        if start >= clock and clock >= end:
            check_player(table, team, player)
            modify_table(table, team, player, '+/-', plusminus[team-1])


def quarter_end(Q, start, end, table, oncourt, plusminus):
    '''
    This function is launched every time a quarter end is detected
    - Q: quarter that has just ended (int)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    for team in range(1,3):
        # we add the minutes of the players that end the quarter (as it is usually done when they are changed)
        for player in oncourt[team-1]:
            interval, _, _ = compute_interval(oncourt[team-1][player], datetime.time(0, 12*(4-Q), 0), start, end)
            if interval != datetime.timedelta():
                check_player(table, team, player)
                modify_table(table, team, player, 'Mins', interval)

        # we delete the variables related to the quarter
        plusminus[team-1] = 0
        oncourt[team-1].clear()


def final_computations(table):
    '''
    This function computes the cumulative value for every category and computes the dependent categories
    Input:
    - table: box score of the teams (list of pandas.DataFrame)
    '''
    for team in range(1,3):
        # computation of the cumulative values:
        table[team-1].loc["TOTAL"] = table[team-1].apply(np.sum)

        # computation of the dependent categories:
        for pl, row in table[team-1].iterrows():
            # computation of 1Pt%, 2Pt% and 3Pt%:
            for i in range(1,4):
                if row[str(i)+'PtA'] != 0:
                    perc = row[str(i)+'PtI']/row[str(i)+'PtA'] * 100
                    table[team-1].loc[pl,str(i)+'Pt%'] = round(perc, 2)
                else:
                    table[team-1].loc[pl,str(i)+'Pt%'] = "-"
            # computation of field goal percentage (FG%):
            if row['2PtA'] + row['3PtA'] != 0:
                perc = (row['2PtI'] + row['3PtI'])/(row['2PtA'] + row['3PtA']) * 100
                table[team-1].loc[pl,'FG%'] = round(perc, 2)
            else:
                table[team-1].loc[pl,'FG%'] = "-"


def correct_plusminus(lines, i, table):
    '''
    This function is launched when there is a scored free throw,
    to check whether there was a change after the corresponding foul.
    In case there was any change, it corrects the +/- of the involving players
    - i: the index of the free throw action (int)
    '''
    ftAction = lines[i].strip().split(", ")
    ftTeam = int(ftAction[1])
    j = i - 1
    action = lines[j].strip().split(", ")
    while not (len(action) > 3 and action[3] == "F"): # we determine whether the action is a foul
        if len(action) > 3 and action[3] == "C": # we determine whether the action is a change
            team, playerOut, playerIn = int(action[1]), action[2], action[4]
            points = 2*(team==ftTeam) - 1  #true -> 1, false -> -1
            modify_table(table, team, playerOut, '+/-', points)
            modify_table(table, team, playerIn, '+/-', -points)
        j -= 1
        action = lines[j].strip().split(", ")


def shoot(i, action, start, end, table, oncourt, plusminus, lines):
    '''
    Treatment of an action that was detected as a shot. It will have the following structure:
        clock team player "S" points [dist] result [A assistant]
    - i: index of the studied line. It will be useful in plays such as free throws (int)
    - action: studied play (list)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    clock, team, player, points = action[0], int(action[1]), action[2], int(action[4])
    clock = time_from_string(clock)
    opTeam = other_team(team)  # team = 1 -> opTeam = 2, team = 2 -> opTeam = 1
    check_oncourt(oncourt, team, player, clock, start, end, table, plusminus)

    if start >= clock and clock >= end:
        check_player(table, team, player)
        modify_table(table, team, player, str(points)+"PtA", 1)
    distGiven = action[5] != "I" and action[5] != "O"
    # distGiven is true if it is neither I nor O. Then in this position we have the distance.
    # Its presence moves the position of the other arguments
    
    result = action[5 + distGiven]
    if result == "I": # the shot was in
        if start >= clock and clock >= end:
            modify_table(table, team, player, str(points)+"PtI", 1)
            modify_table(table, team, player, 'Pts', points)
            plusminus[team-1] += points
            for pl in oncourt[team-1]: #modificacion of the +/- of the scoring team
                check_player(table, team, pl)
                modify_table(table, team, pl, '+/-', points)
            plusminus[opTeam-1] -= points
            for pl in oncourt[opTeam-1]: #modificacion of the +/- of the opposite team
                check_player(table, opTeam, pl)
                modify_table(table, opTeam, pl, '+/-', -points)
            
            if points == 1: # we must check whether there was a miscalculation of +/-
                correct_plusminus(lines, i, table)

        if len(action) == 8+distGiven and action[6+distGiven] == "A": # there is an assist
            assistant = action[7+distGiven]
            check_oncourt(oncourt, team, assistant, clock, start, end, table, plusminus)
            if start >= clock and clock >= end:
                check_player(table, team, assistant)
                modify_table(table, team, assistant, 'Ast', 1)
                modify_table(table, team, assistant, str(points)+'PtAst', 1)
                modify_table(table, team, player, 'AstPts', points)


def rebound(action, start, end, table, oncourt, plusminus):
    '''
    Treatment of an action that was detected as a rebound. It will have the following structure:
        clock team player "R" kind
    - action: studied play (list)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    clock, team, player, kind = action[0], int(action[1]), action[2], action[4]
    clock = time_from_string(clock)
    check_oncourt(oncourt, team, player, clock, start, end, table, plusminus)

    if start >= clock and clock >= end:
        check_player(table, team, player)
        modify_table(table, team, player, 'TR', 1)
        modify_table(table, team, player, kind+"R", 1)


def turnover(action, start, end, table, oncourt, plusminus):
    '''
    Treatment of an action that was detected as a simple turnover. It will have the following structure:
        clock team player "T"
    - action: studied play (list)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    clock, team, player = action[0], int(action[1]), action[2]
    clock = time_from_string(clock)
    check_oncourt(oncourt, team, player, clock, start, end, table, plusminus)

    if start >= clock and clock >= end:
        check_player(table, team, player)
        modify_table(table, team, player, 'To', 1)


def steal(action, start, end, table, oncourt, plusminus):
    '''
    Treatment of an action that was detected as a steal. It will have the following structure:
        clock team player "St" receiver
    - action: studied play (list)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    clock, team, player, opPlayer = action[0], int(action[1]), action[2], action[4]
    clock = time_from_string(clock)
    check_oncourt(oncourt, team, player, clock, start, end, table, plusminus)
    opTeam = other_team(team)  # team = 1 -> opTeam = 2, team = 2 -> opTeam = 1
    check_oncourt(oncourt, opTeam, opPlayer, clock, start, end, table, plusminus)

    if start >= clock and clock >= end:
        check_player(table, team, player)
        modify_table(table, team, player, 'St', 1)
        check_player(table, opTeam, opPlayer)
        modify_table(table, opTeam, opPlayer, 'To', 1)


def block(action, start, end, table, oncourt, plusminus):
    '''
    Treatment of an action that was detected as a block. It will have the following structure:
        clock team player "B" receiver points
    - action: studied play (list)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    clock, team, player, opPlayer, points = action[0], int(action[1]), action[2], action[4], action[5]
    clock = time_from_string(clock)
    check_oncourt(oncourt, team, player, clock, start, end, table, plusminus)
    
    opTeam = other_team(team)  # team == 1 -> opTeam = 2,  team == 2 -> opTeam = 1
    check_oncourt(oncourt, opTeam, opPlayer, clock, start, end, table, plusminus)
    
    if start >= clock and clock >= end:
        check_player(table, team, player)
        modify_table(table, team, player, 'Bl', 1)
        check_player(table, opTeam, opPlayer)
        modify_table(table, opTeam, opPlayer, points+"PtA", 1)


def foul(action, start, end, table, oncourt, plusminus):
    '''
    Treatment of an action that was detected as a foul. It will have the following structure:
        clock team player "F" kind [receiver]
    - action: studied play (list)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    clock, team, player, kind = action[0], int(action[1]), action[2], action[4]
    clock = time_from_string(clock)
    check_oncourt(oncourt, team, player, clock, start, end, table, plusminus)
    
    if start >= clock and clock >= end:
        check_player(table, team, player)
        modify_table(table, team, player, 'FM', 1)
        if kind == "O":
            modify_table(table, team, player, 'To', 1)

    if len(action) == 6: # there is a player from the opposite team that receives the foul
        opPlayer = action[5]
        opTeam = other_team(team)
        check_oncourt(oncourt, opTeam, opPlayer, clock, start, end, table, plusminus)
        if start >= clock and clock >= end:
            check_player(table, opTeam, opPlayer)
            modify_table(table, opTeam, opPlayer, 'FR', 1)


def change(action, start, end, table, oncourt, plusminus):
    '''
    Treatment of an action that was detected as a change. It will have the following structure:
        clock team playerOut "C" playerIn
    - action: studied play (list)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    clock, team, playerOut, playerIn = action[0], int(action[1]), action[2], action[4]
    clock = time_from_string(clock)
    check_oncourt(oncourt, team, playerOut, clock, start, end, table, plusminus)

    interval, _, _ = compute_interval(oncourt[team-1][playerOut], clock, start, end)
    if interval != datetime.timedelta(): # if it is equal, the interval is null (there is no overlap)
        check_player(table, team, playerOut)
        modify_table(table, team, playerOut, 'Mins', interval)
        check_player(table, team, playerIn)
        
    del oncourt[team-1][playerOut]
    oncourt[team-1][playerIn] = clock


def treat_line(lines, i, line, prevQ, start, end, table, oncourt, plusminus, others):
    '''
    This function is launched to detect the type of play an action is
    - i: index of the studied line. It will be useful in plays such as free throws (int)
    - line: studied line (string)
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    action = line.split(", ")
    
    #we need to check whether there was a change of quarter
    clock = action[0]
    clock = time_from_string(clock)
    Q = get_quarter(clock)
    if prevQ != Q:
        quarter_end(prevQ, start, end, table, oncourt, plusminus)
    prevQ = Q
    
    # classification of the action
    if len(action) > 3 and action[3] == "S":
        shoot(i, action, start, end, table, oncourt, plusminus, lines)
    elif len(action) > 3 and action[3] == "R":
        rebound(action, start, end, table, oncourt, plusminus)
    elif len(action) > 3 and action[3] == "T":
        turnover(action, start, end, table, oncourt, plusminus)
    elif len(action) > 3 and action[3] == "St":
        steal(action, start, end, table, oncourt, plusminus)
    elif len(action) > 3 and action[3] == "B":
        block(action, start, end, table, oncourt, plusminus)
    elif len(action) > 3 and action[3] == "F":
        foul(action, start, end, table, oncourt, plusminus)
    elif len(action) > 3 and action[3] == "C":
        change(action, start, end, table, oncourt, plusminus)
    else:
        if start >= clock and clock >= end:
            others.append(action)
    return Q


def read_plays(f, start, end, table, oncourt, plusminus, others):
    '''
    This function launches the sequential analysis of sentences
    - f: file object with the PbP in the standard format
    - start: starting time of the boxscore compution interval (string)
    - end: ending time of the boxscore compution interval (string)
    '''
    Q = 1
    lines = f.readlines()
    for i, line in enumerate(lines):
        line = line.strip()
        Q = treat_line(lines, i, line, Q, start, end, table, oncourt, plusminus, others)


def main(file, start = "48:00", end = "00:00"):
    '''
    This function builds the boxscores (stored in table)
    '''
    global categories
    categories = ['Mins', '2PtI', '2PtA', '2Pt%', '3PtI', '3PtA', '3Pt%', 'FG%', '1PtI', '1PtA', '1Pt%', 'OR', 'DR', 'TR', '2PtAst', '3PtAst', 'Ast', 'Bl', 'St', 'To', 'FM', 'FR', 'AstPts', 'Pts', '+/-']
    os.chdir(os.path.dirname(__file__))

    start = time_from_string(start)
    end = time_from_string(end)

    # tables where the boxscore of the local and visiting team will be computed respectively:
    table = [pd.DataFrame(columns = categories).astype({'Mins': 'datetime64[ns]', '2Pt%': 'float'})] * 2
    # dictionaries that will hold the local and visiting players respectively at a specific time:
    oncourt = [{}, {}]
    # integers where the plusminus of the local and visiting team will be stored:
    plusminus = [0, 0]
    # list that will store the plays not used for the boxscore computation:
    others = []

    with open(file, encoding="utf-8") as f:
        read_plays(f, start, end, table, oncourt, plusminus, others)

    quarter_end(4, start, end, table, oncourt, plusminus)
    final_computations(table)

    return table