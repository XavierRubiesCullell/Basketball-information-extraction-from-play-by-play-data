'''
f = open('./Prova.txt', 'r')
print(f.read())
for line in f:
    # reading each word         
    for word in line.split(): 
        # displaying the action            
        print(word)
'''
'''
with open('some.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
'''

import numpy as np
import pandas as pd
import datetime
import os
import csv
import time


def shoot(play, new_line):
    '''
    Per a trobar la distància de tir:
    x = re.search("(\d+)(?!.*\d).+?(?=ft)", txt)
    print(x.group(1))
    '''

    if "(block" in play:
        new_line[1] = str((int(new_line[1])*5)%3)
        ind = play.index("(block")
        new_line.append(play[ind+2] + " " + play[ind+3][:-1])
        new_line.append('B')
        new_line.append(play[0] + " " + play[1])
        new_line.append(play[3][0])
    
    else:
        player = play[0] + " " + play[1]
        new_line.append(player)
        new_line.append('S')
    
        if play[3] == "free":
            new_line.append('1')
        else: # 2 or 3-point shot
            new_line.append(play[3][0])

        if play[2] == "makes":
            new_line.append('I')
            try:
                index = play.index("(assist")
                new_line.append('A')
                new_line.append(play[index+2] + " " +play[index+3][:-1])
            except ValueError:
                pass

        else:
            new_line.append('O')
    return new_line


def rebound(play, new_line):
    if play[3] == "Team":
        player = '-'
    else:
        player = play[3] + " " + play[4]
    new_line.append(player)

    new_line.append('R')
    if play[0] == "Defensive":
        new_line.append('D')
    else:
        new_line.append('O')
    return new_line


def turnover(play, new_line):
    if "foul)" in play:
        new_line = ""
        return new_line
    if "steal" in play:
        new_line[1] = str((int(new_line[1])*5)%3)
        ind = play.index("steal")
        new_line.append(play[ind+2] + " " + play[ind+3][:-1])
        new_line.append("St")
        new_line.append(play[2] + " " + play[3])
        return new_line
    else:
        if play[2] == "Team":
            player = '-'
        else:
            player = play[2] + " " + play[3]
        new_line.append(player)
        new_line.append("T")
        return new_line


def foul(play,new_line):
    ind = play.index("foul")
    new_line.append(play[ind+2] + " " + play[ind+3])
    new_line.append("F")
    if play[ind-1] == "Offensive":
        new_line.append("O")
    else:
        if play[0]+" "+play[1] != "Loose ball":
            new_line[1] = str((int(new_line[1])*5)%3)
        new_line.append("D")

    ind = play.index("(drawn")
    new_line.append(play[ind+2] + " " + play[ind+3][:-1])
    return new_line


def change(play, new_line):
    playerOut = play[6] + " " + play[7]
    playerIn = play[0] + " " + play[1]
    new_line += [playerOut, "C", playerIn]
    return new_line


def treat_play(play, new_line):
    play = play.split()
    if play[2] == "makes" or play[2] == "misses":
        return shoot(play, new_line)
    if play[1] == "rebound":
        return rebound(play, new_line)
    if play[0] == "Turnover":
        return turnover(play, new_line)
    if "foul" in play:
        return foul(play, new_line)
    if play[2] == "enters":
        return change(play, new_line)
    if "timeout" in play:
        new_line.append("Timeout")
        return new_line
    if "Replay" in play:
        new_line.append("Instant Replay")
        return new_line
    return "STILL NOT TREATED"


def treat_action(action, Q, out):
    new_line = []

    clock = action[0]
    clock = datetime.datetime.strptime(clock, "%M:%S.%f")
    quarter_time = datetime.timedelta(minutes = 12*(4-Q))
    clock = clock + quarter_time
    new_line.append(clock.strftime("%M:%S"))

    if action[1] != '':
        new_line.append("2")
        play = action[1]
    else:
        new_line.append("1")
        play = action[5]
    
    #print(action)
    new_line = treat_play(play, new_line)
    #print(" ".join(new_line))
    if new_line != "":
        out.write(", ".join(new_line) + '\n')


def treat_line(action, Q, out):
    try: # the except will be executed if the line is a header (it has no time)
        clock = action[0]
        datetime.datetime.strptime(clock, "%M:%S.%f")

        try: # we remove the .0 in the time in case it is included
            clock = clock[:clock.index('.')]

            if (len(action) == 6): # the action will be an in-game action
                treat_action(action, Q, out)
            else:
                neutral_actions.append(action)
                if clock == "12:00":
                    Q = Q + 1
                
        except ValueError:
            pass

    except ValueError: 
        non_actions.append(action)

    return Q
    

def main(in_file):
    os.chdir(os.path.dirname(__file__))

    global actions
    actions = []
    global neutral_actions
    neutral_actions = []
    global non_actions
    non_actions = []
    Q = 0

    out = open("OutputStandardPbP.txt", "x", encoding="utf8")
    with open(in_file, encoding="utf8", errors="ignore") as f:
        reader = csv.reader(f)
        
        for i, row in enumerate(reader):
            Q = treat_line(row, Q, out)
    out.close()

    print("Neutral actions:")
    for el in neutral_actions:
        print (el)
    print("\nOthers:")
    for el in non_actions:
        print (el)


main('BasketballReferencePbP.txt')