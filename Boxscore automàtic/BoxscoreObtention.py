# f = open('./Prova.txt', 'r')
# print(f.read())
    # for line in f:
    #     # reading each word         
    #     for word in line.split(): 
    #         # displaying the action            
    #         print(word)

import numpy as np
import pandas as pd
import datetime
import os


def check_player(team, player):
    if player not in set(globals()["table"+team].index):
        new_row = [datetime.timedelta()] + [0]*(len(categories)-1) #new_row = ["48:00"] + [0]*(len(categories)-1)
        new_row = pd.Series(new_row, index=categories, name=player)
        globals()["table"+team] = globals()["table"+team].append(new_row)

def check_oncourt(team, player, Q):
    if player != '-' and player not in globals()["oncourt"+team]:
        #globals()["oncourt"+team][player] = datetime.timedelta(minutes = 48)
        globals()["oncourt"+team][player] = datetime.time(0, (5-Q)*12, 0)
        globals()["table"+team].loc[player,"+/-"] += globals()["plusminus"+team]


def shoot(action, Q):
    # clock team player points [dist] result [A assistant]
    clock, team, player, points = action[0], action[1], action[2], action[4]
    op_team = str((int(team)*5)%3)  # team = 1 -> op_team = 2, team = 2 -> op_team = 1
    check_player(team, player)
    check_oncourt(team, player, Q)

    globals()["table"+team].loc[player,points+"ptA"] += 1
    dist_given = action[5] != 'I' and action[5] != 'O' # true if it is not I or O, so it is the number expressing the distance
    result = action[5 + dist_given]

    if result == 'I':
        globals()["table"+team].loc[player,points+"ptI"] += 1
        globals()["table"+team].loc[player,"Pts"] += int(points)
        globals()["plusminus"+team] += int(points)
        for pl in globals()["oncourt"+team]:
            globals()["table"+team].loc[pl,"+/-"] += int(points)
        globals()["plusminus"+op_team] -= int(points)
        for pl in globals()["oncourt"+op_team]:
            globals()["table"+op_team].loc[pl,"+/-"] -= int(points)

        if len(action) == 8+dist_given and action[6+dist_given] == 'A': # there is an assist
            assistant = action[7+dist_given]
            check_player(team, assistant)
            check_oncourt(team, assistant, Q)
            globals()["table"+team].loc[assistant,"Ast"] += 1


def rebound(action, Q):
    clock, team, player, kind = action[0], action[1], action[2], action[4]
    check_player(team, player)
    check_oncourt(team, player, Q)

    globals()["table"+team].loc[player,"Reb"] += 1
    globals()["table"+team].loc[player,kind+"R"] += 1


def turnover(action, Q):
    clock, team, player = action[0], action[1], action[2]
    check_player(team, player)
    check_oncourt(team, player, Q)

    globals()["table"+team].loc[player,"To"] += 1


def steal(action, Q):
    clock, team, player, op_player = action[0], action[1], action[2], action[4]
    check_player(team, player)
    check_oncourt(team, player, Q)

    globals()["table"+team].loc[player,"St"] += 1
    op_team = str((int(team)*5)%3)  # team = 1 -> op_team = 2, team = 2 -> op_team = 1
    check_player(op_team, op_player)
    check_oncourt(op_team, op_player, Q)
    globals()["table"+str(op_team)].loc[op_player,"To"] += 1


def block(action, Q):
    clock, team, player, op_player, points = action[0], action[1], action[2], action[4], action[5]
    check_player(team, player)
    check_oncourt(team, player, Q)

    globals()["table"+team].loc[player,"Bl"] += 1
    op_team = str((int(team)*5)%3)  # team = 1 -> op_team = 2, team = 2 -> op_team = 1
    check_player(op_team, op_player)
    check_oncourt(op_team, op_player, Q)
    globals()["table"+op_team].loc[op_player,points+"ptA"] += 1


def foul(action, Q):
    clock, team, player, kind = action[0], action[1], action[2], action[4]
    check_player(team, player)
    check_oncourt(team, player, Q)
    
    globals()["table"+team].loc[player,"FM"] += 1
    if kind == 'O':
        globals()["table"+team].loc[player,"To"] += 1

    if len(action) == 6:
        op_player = action[5]
        op_team = str((int(team)*5)%3)
        check_player(op_team, op_player)
        check_oncourt(op_team, op_player, Q)
        globals()["table"+op_team].loc[op_player,"FR"] += 1


def change(action, Q):
    clock, team, playerOut, playerIn = action[0], action[1], action[2], action[4]
    check_player(team, playerOut)
    check_oncourt(team, playerOut, Q)
    check_player(team, playerIn)

    clock = clock.split(":")
    #clock = datetime.timedelta(minutes = int(clock[0]), seconds = int(clock[1]))
    clock = datetime.time(0, int(clock[0]), int(clock[1]))
    #interval = globals()["oncourt"+team][playerOut] - clock
    aux_oncourt = datetime.datetime.combine(my_date, globals()["oncourt"+team][playerOut])
    aux_clock = datetime.datetime.combine(my_date, clock)
    interval = aux_oncourt - aux_clock
    globals()["table"+team].loc[playerOut,'Mins'] += interval
    del globals()["oncourt"+team][playerOut]
    globals()["oncourt"+team][playerIn] = clock


def quarter_end(Q):
    for pl in oncourt1:
        #table1.loc[pl,'Mins'] += oncourt1[pl]
        interval = datetime.datetime.combine(my_date, oncourt1[pl]) - datetime.datetime.combine(my_date, datetime.time(0, 12*(4-Q), 0))
        table1.loc[pl,'Mins'] += interval

    for pl in oncourt2:
        #table2.loc[pl,'Mins'] += oncourt2[pl]
        interval = datetime.datetime.combine(my_date, oncourt2[pl]) - datetime.datetime.combine(my_date, datetime.time(0, 12*(4-Q), 0))
        table2.loc[pl,'Mins'] += interval

    global plusminus1, plusminus2
    plusminus1 = 0
    plusminus2 = 0
    oncourt1.clear()
    oncourt2.clear()


def treat_line(line, prev_Q):
    action = line.split(", ")
    
    #we need to check whether there was a change of quarter
    clock = action[0]
    clock = clock.split(":")
    clock = datetime.time(0, int(clock[0]), int(clock[1]))
    Q = (4-int(clock.minute/12))
    if prev_Q != Q:
        quarter_end(prev_Q)

    #print(action)
    #if Q >= 3:
    if len(action) > 3 and action[3] == "S":
        shoot(action, Q)
    elif len(action) > 3 and action[3] == "R":
        rebound(action, Q)
    elif len(action) > 3 and action[3] == "T":
        turnover(action, Q)
    elif len(action) > 3 and action[3] == "St":
        steal(action, Q)
    elif len(action) > 3 and action[3] == "B":
        block(action, Q)
    elif len(action) > 3 and action[3] == "F":
        foul(action, Q)
    elif len(action) > 3 and action[3] == "C":
        change(action, Q)
    else:
        others.append(action)
    
    # if Q == 3 and len(action) > 3 and action[3] == "S":
    #     print(action)
    #     print(oncourt1.keys())
    #     print(table1['+/-'])
    #     print(plusminus1)
    #     print()

    return Q


def initalise():
    global categories
    categories = ['Mins', '+/-', 'Pts', '2ptI', '2ptA', '3ptI', '3ptA', '1ptI', '1ptA', 'OR', 'DR', 'Reb', 'Ast', 'Bl', 'St', 'To', 'FM', 'FR']
    
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

    global my_date
    my_date = datetime.date(1, 1, 1)

    global others
    others = []


def read_plays(f):
    Q = 1
    for i, line in enumerate(f):
        line = line.strip()
        Q = treat_line(line, Q)


def print_results():
    print("Home team table")
    print(table1)
    print("\nAway team table")
    print(table2)
    print("\nOther actions:")
    for el in others:
        print(el)


def BoxscoreObtentionMain(in_file, pkl1, pkl2):
    os.chdir(os.path.dirname(__file__))

    initalise()

    with open("Files/" + in_file, encoding="utf-8") as f:
        read_plays(f)

    quarter_end(4)
    global table1, table2
    # globals()["table1"] = globals()["table1"].reindex(["I.Okoro", "C.Osman", "A.Drummond", "D.Dotson", "L.Nance", "L.Stevens", "J.McGee", "D.Wade", "T.Maker", "-"])
    # globals()["table2"] = globals()["table2"].reindex(["B.Clarke", "D.Brooks", "K.Anderson", "J.Valančiūnas", "T.Jones", "D.Bane", "D.Melton", "X.Tillman", "G.Dieng", "G.Allen", "-"])
    # table1 = table1.reindex(["I. Okoro", "C. Osman", "A. Drummond", "D. Dotson", "L. Nance", "L. Stevens", "J. McGee", "D. Wade", "T. Maker", "-"])
    # table2 = table2.reindex(["B. Clarke", "D. Brooks", "K. Anderson", "J. Valančiūnas", "T. Jones", "D. Bane", "D. Melton", "X. Tillman", "G. Dieng", "G. Allen", "-"])

    table1.loc["TOTAL"] = table1.apply(np.sum)
    table2.loc["TOTAL"] = table2.apply(np.sum)

    table1.to_pickle("Files/" + pkl1)
    table2.to_pickle("Files/" + pkl2)
    print_results()
    