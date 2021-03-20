import numpy as np
import pandas as pd
import datetime
import os


def computeinterval(in_time, out_time, start, end):
    my_date = datetime.date(1, 1, 1)

    int_start = min(in_time, start)
    int_end = max(out_time, end)
    date_int_start = datetime.datetime.combine(my_date, int_start)
    date_int_end = datetime.datetime.combine(my_date, int_end)
    null = datetime.timedelta() # in case the interval is negative
    return max(date_int_start - date_int_end, null), int_start, int_end


def timefromstring(clock):
    clock = clock.split(":")
    return datetime.time(0, int(clock[0]), int(clock[1]))


def check_player(team, player):
    if player not in set(globals()["table"+team].index):
        new_row = [datetime.timedelta()] + [0]*(len(categories)-1)
        new_row = pd.Series(new_row, index=categories, name=player)
        globals()["table"+team] = globals()["table"+team].append(new_row)


def check_oncourt(team, player, Q, clock, start, end):
    if player != '-' and player not in globals()["oncourt"+team]:
        globals()["oncourt"+team][player] = datetime.time(0, (5-Q)*12, 0)
        if start >= clock and clock >= end:
            check_player(team, player)
            modify_table(team, player, '+/-', globals()["plusminus"+team])


def modify_table(team, player, variable, value):
    globals()["table"+team].loc[player,variable] += value


def correct_plusminus(i):
    ft_action = lines[i].strip().split(", ")
    j = i - 1
    action = lines[j].strip().split(", ")
    while not (len(action) > 3 and action[3] == "F"): # we determine whether the action is a foul
        if len(action) > 3 and action[3] == "C": # we determine whether the action is a change
            team, playerOut, playerIn = action[1], action[2], action[4]
            points = 2*(team==ft_action[1]) - 1  #true -> 1, false -> -1
            modify_table(team, playerOut, '+/-', points)
            modify_table(team, playerIn, '+/-', -points)
        j -= 1
        action = lines[j].strip().split(", ")


def shoot(i, action, Q, start, end):
    # clock team player points [dist] result [A assistant]
    clock, team, player, points = action[0], action[1], action[2], action[4]
    clock = timefromstring(clock)
    op_team = str((int(team)*5)%3)  # team = 1 -> op_team = 2, team = 2 -> op_team = 1
    check_oncourt(team, player, Q, clock, start, end)

    if start >= clock and clock >= end:
        check_player(team, player)
        modify_table(team, player, points+"ptA", 1)
    dist_given = action[5] != "I" and action[5] != "O" # true if it is not I or O, so it is the number expressing the distance
    result = action[5 + dist_given]

    if result == "I":
        if start >= clock and clock >= end:
            modify_table(team, player, points+"ptI", 1)
            modify_table(team, player, 'Pts', int(points))
            globals()["plusminus"+team] += int(points)
            for pl in globals()["oncourt"+team]:
                check_player(team, pl)
                modify_table(team, pl, '+/-', int(points))
            globals()["plusminus"+op_team] -= int(points)
            for pl in globals()["oncourt"+op_team]:
                check_player(op_team, pl)
                modify_table(op_team, pl, '+/-', -int(points))
            
            if points == "1":
                correct_plusminus(i)

        if len(action) == 8+dist_given and action[6+dist_given] == "A": # there is an assist
            assistant = action[7+dist_given]
            check_oncourt(team, assistant, Q, clock, start, end)
            if start >= clock and clock >= end:
                check_player(team, assistant)
                modify_table(team, assistant, 'Ast', 1)


def rebound(action, Q, start, end):
    clock, team, player, kind = action[0], action[1], action[2], action[4]
    clock = timefromstring(clock)
    check_oncourt(team, player, Q, clock, start, end)

    if start >= clock and clock >= end:
        check_player(team, player)
        modify_table(team, player, 'Reb', 1)
        modify_table(team, player, kind+"R", 1)


def turnover(action, Q, start, end):
    clock, team, player = action[0], action[1], action[2]
    clock = timefromstring(clock)
    check_oncourt(team, player, Q, clock, start, end)

    if start >= clock and clock >= end:
        check_player(team, player)
        modify_table(team, player, 'To', 1)


def steal(action, Q, start, end):
    clock, team, player, op_player = action[0], action[1], action[2], action[4]
    clock = timefromstring(clock)
    check_oncourt(team, player, Q, clock, start, end)
    op_team = str((int(team)*5)%3)  # team = 1 -> op_team = 2, team = 2 -> op_team = 1
    check_oncourt(op_team, op_player, Q, clock, start, end)

    if start >= clock and clock >= end:
        check_player(team, player)
        modify_table(team, player, 'St', 1)
        check_player(op_team, op_player)
        modify_table(op_team, op_player, 'To', 1)


def block(action, Q, start, end):
    clock, team, player, op_player, points = action[0], action[1], action[2], action[4], action[5]
    clock = timefromstring(clock)
    check_oncourt(team, player, Q, clock, start, end)
    
    op_team = str((int(team)*5)%3)  # team == 1 -> op_team = 2,  team == 2 -> op_team = 1
    check_oncourt(op_team, op_player, Q, clock, start, end)
    
    if start >= clock and clock >= end:
        check_player(team, player)
        modify_table(team, player, 'Bl', 1)
        check_player(op_team, op_player)
        modify_table(op_team, op_player, points+"ptA", 1)


def foul(action, Q, start, end):
    clock, team, player, kind = action[0], action[1], action[2], action[4]
    clock = timefromstring(clock)
    check_oncourt(team, player, Q, clock, start, end)
    
    if start >= clock and clock >= end:
        check_player(team, player)
        modify_table(team, player, 'FM', 1)
        if kind == "O":
            modify_table(team, player, 'To', 1)

    if len(action) == 6:
        op_player = action[5]
        op_team = str((int(team)*5)%3)
        check_oncourt(op_team, op_player, Q, clock, start, end)
        if start >= clock and clock >= end:
            check_player(op_team, op_player)
            globals()["table"+op_team].loc[op_player,"FR"] += 1


def change(action, Q, start, end):
    clock, team, playerOut, playerIn = action[0], action[1], action[2], action[4]
    clock = timefromstring(clock)
    check_oncourt(team, playerOut, Q, clock, start, end)

    interval, int_min, int_max = computeinterval(globals()["oncourt"+team][playerOut], clock, start, end)
    if interval != datetime.timedelta(): # if it is equal, the interval is null (there is no overlap)
        check_player(team, playerOut)
        modify_table(team, playerOut, 'Mins', interval)
        check_player(team, playerIn)
        if playerOut not in globals()["playintervals"+team].keys():
            globals()["playintervals"+team][playerOut] = []
        globals()["playintervals"+team][playerOut].append((int_min.strftime("%M:%S"), int_max.strftime("%M:%S")))
    del globals()["oncourt"+team][playerOut]
    globals()["oncourt"+team][playerIn] = clock


def quarter_end(Q, start, end):
    for player in oncourt1:
        interval, int_min, int_max = computeinterval(oncourt1[player], datetime.time(0, 12*(4-Q), 0), start, end)
        if interval != datetime.timedelta():
            check_player("1", player)
            table1.loc[player,'Mins'] += interval
            if player not in playintervals1.keys():
                playintervals1[player] = []
            playintervals1[player].append((int_min.strftime("%M:%S"), int_max.strftime("%M:%S")))

    for player in oncourt2:
        interval, int_min, int_max = computeinterval(oncourt2[player], datetime.time(0, 12*(4-Q), 0), start, end)
        if interval != datetime.timedelta():
            check_player("2", player)
            table2.loc[player,'Mins'] += interval
            if player not in playintervals2.keys():
                playintervals2[player] = []
            playintervals2[player].append((int_min.strftime("%M:%S"), int_max.strftime("%M:%S")))

    global plusminus1, plusminus2
    plusminus1 = 0
    plusminus2 = 0
    oncourt1.clear()
    oncourt2.clear()


def treat_line(i, line, prev_Q, start, end):
    action = line.split(", ")
    
    #we need to check whether there was a change of quarter
    clock = action[0]
    clock = timefromstring(clock)
    Q = (4-int(clock.minute/12))
    if prev_Q != Q:
        quarter_end(prev_Q, start, end)

    if len(action) > 3 and action[3] == "S":
        shoot(i, action, Q, start, end)
    elif len(action) > 3 and action[3] == "R":
        rebound(action, Q, start, end)
    elif len(action) > 3 and action[3] == "T":
        turnover(action, Q, start, end)
    elif len(action) > 3 and action[3] == "St":
        steal(action, Q, start, end)
    elif len(action) > 3 and action[3] == "B":
        block(action, Q, start, end)
    elif len(action) > 3 and action[3] == "F":
        foul(action, Q, start, end)
    elif len(action) > 3 and action[3] == "C":
        change(action, Q, start, end)
    else:
        if start >= clock and clock >= end:
            others.append(action)

    return Q


def initalise():
    global categories
    categories = ['Mins', '2ptI', '2ptA', '3ptI', '3ptA', '1ptI', '1ptA', 'OR', 'DR', 'Reb', 'Ast', 'Bl', 'St', 'To', 'FM', 'FR', 'Pts', '+/-']
    
    global table1, table2
    table1 = pd.DataFrame(columns = categories)
    table2 = pd.DataFrame(columns = categories)
    table1 = table1.astype({'Mins': 'datetime64[ns]'})
    table2 = table2.astype({'Mins': 'datetime64[ns]'})

    global plusminus1, plusminus2
    plusminus1 = 0
    plusminus2 = 0

    global oncourt1, oncourt2
    oncourt1 = {}
    oncourt2 = {}

    global playintervals1, playintervals2
    playintervals1 = {}
    playintervals2 = {}

    global others
    others = []


def read_plays(f, start, end):
    Q = 1
    global lines
    lines = f.readlines()
    for i, line in enumerate(lines):
        line = line.strip()
        Q = treat_line(i, line, Q, start, end)


def print_results():
    print("Home team table")
    print(table1)
    print("\nAway team table")
    print(table2)
    print()
    for player in playintervals1.items():
        print(player)
    print()
    for player in playintervals2.items():
        print(player)
    print("\nOther actions:")
    for el in others:
        print(el)


def BoxscoreObtentionMain(in_file, pkl1, pkl2, start="48:00", end="0:00"):
    os.chdir(os.path.dirname(__file__))

    initalise()

    start = timefromstring(start)
    end = timefromstring(end)

    with open("Files/" + in_file, encoding="utf-8") as f:
        read_plays(f, start, end)

    quarter_end(4, start, end)
    # global table1, table2
    # table1 = table1.reindex(["I. Okoro", "C. Osman", "A. Drummond", "D. Dotson", "L. Nance", "L. Stevens", "J. McGee", "D. Wade", "T. Maker", "-"])
    # table2 = table2.reindex(["B. Clarke", "D. Brooks", "K. Anderson", "J. Valančiūnas", "T. Jones", "D. Bane", "D. Melton", "X. Tillman", "G. Dieng", "G. Allen", "-"])

    table1.loc["TOTAL"] = table1.apply(np.sum)
    table2.loc["TOTAL"] = table2.apply(np.sum)

    table1.to_pickle("Files/" + pkl1)
    table2.to_pickle("Files/" + pkl2)
    print_results()