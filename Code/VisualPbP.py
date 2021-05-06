from Functions import *
import time
import datetime
import math

def get_clock(i, lines):
    action = lines[i]
    action = action.split(", ")
    return action[0]

def interval(tBefore, tNow):
    tBefore = time_from_string(tBefore)
    tNow = time_from_string(tNow)
    diff = tBefore - tNow
    diff = diff.seconds
    diff == max(diff, 1)
    return math.exp(-math.pow(diff,2) / (2*math.pow(9,2)))


def next_time(t):
    quarter, minutes, seconds = t.split(":")
    if minutes == "00" and seconds == "00":
        if quarter[1] == "O" or quarter[0] == "4":
            minutes = "05"
        else:
            minutes = "12"
        return next_quarter(quarter) + ":" + minutes + ":" + seconds
    
    clock = datetime.datetime.strptime(minutes+":"+seconds, "%M:%S")
    clock -= datetime.timedelta(seconds=1)
    return quarter + ":" + clock.strftime("%M:%S")

def show_header(t, score):
    print(t,score)

def show_action(action):
    if action == "black":
        print("\n")
    else:
        print(action.strip().split(", ")[1:], "\n")

def update_score(line, score):
    action = line.strip().split(", ")
    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team = int(action[1])
            points = int(action[4])
            score[team-1] += points

def treat_second(tNow, lineId, lines, score, lastQ):
    nLines = len(lines)
    if lineId == 0:
        clockBefore = "1Q:12:00"
        clockNext = get_clock(lineId, lines)
    elif lineId == nLines:
        clockBefore = get_clock(lineId-1, lines)
        clockNext = lastQ+":00:00"
    else:
        clockBefore = get_clock(lineId-1, lines)
        clockNext = get_clock(lineId, lines)
    t = interval(clockBefore, clockNext)
    time.sleep(t)

    show_header(tNow, score)
    if clockNext == tNow and lineId < nLines:
        show_action(lines[lineId])
        update_score(lines[lineId], score)
        
        lineId += 1
    else:
        show_action("black")
        
    if lineId >= nLines-1 or get_clock(lineId-1, lines) != get_clock(lineId, lines):
        tNow = next_time(tNow)

    return tNow, lineId

def main(file, lastQ):
    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    tNow = "1Q:12:00"
    score = [0, 0]
    lineId = 0
    while time_from_string(tNow) >= time_from_string(lastQ+":00:00"):
        tNow, lineId = treat_second(tNow, lineId, lines, score, lastQ)