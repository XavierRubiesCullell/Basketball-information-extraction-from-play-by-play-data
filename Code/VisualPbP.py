import time
import datetime
import math
import PIL.Image
import base64
import io
import PySimpleGUI as sg

from Functions import *

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
    return math.exp(-math.pow(diff,2) / (2*math.pow(5,2)))

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

def convert_to_bytes(file_or_bytes, resize=None):
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()

def show_header(t, score, window):
    if window is None:
        print(t, score, sep="        ")
    else:
        window['Clock'].update(value=t)
        window['Score1'].update(value=score[0])
        window['Score2'].update(value=score[1])

def show_action(action, window, imageFolder):
    if action == "black":
        if window is None:
            print("\n")
        else:
            window['ActionText'].update(str(""))
            window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Black.jpg", resize=(200,200)))
    else:
        if window is None:
            print(action.strip().split(", ")[1:], "\n")
        else:
            window['ActionText'].update(str(action.strip().split(", ")[1:]))
            actionType = action.strip().split(", ")[3]
            if actionType == "S":
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=(200,200)))
            elif actionType == "R":
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=(200,200)))
            elif actionType == "T":
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=(200,200)))
            elif actionType == "St":
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=(200,200)))
            elif actionType == "B":
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=(200,200)))
            elif actionType == "F":
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=(200,200)))
            elif actionType == "C":
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=(200,200)))


def update_score(line, score):
    action = line.strip().split(", ")
    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team = int(action[1])
            points = int(action[4])
            score[team-1] += points


def pause(window):
    window['Pause/Resume'].update("Resume")
    while True:
        event, _ = window.read()
        if event == 'Pause/Resume':
            window['Pause/Resume'].update("Pause")
            break
        elif event == sg.WIN_CLOSED:
            window.close()
            break


def treat_second(tNow, prevAction, lineId, lines, score, lastQ, window, imageFolder):
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
    if prevAction != "black":
        start = time.time()
        while time.time() - start < 2:
            if window is not None:
                event, _ = window.read(timeout=25)
                if event == 'Pause/Resume':
                    pause(window)

    show_header(tNow, score, window)
    if tNow == clockNext and lineId < nLines:
        action = lines[lineId]
        update_score(action, score)
        lineId += 1
    else:
        action = "black"
    show_action(action, window, imageFolder)
        
    if lineId >= nLines-1 or get_clock(lineId-1, lines) != get_clock(lineId, lines):
        tNow = next_time(tNow)

    return tNow, lineId, action


def main(file, lastQ, window=None, imageFolder="VisualPbPImages"):
    os.chdir(os.path.dirname(__file__))
    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    tNow = "1Q:12:00"
    score = [0, 0]
    lineId = 0
    action = "black"

    while time_from_string(tNow) >= time_from_string(lastQ+":00:00"):
        if window is not None:
            event, _ = window.read(timeout=25)
            if event == 'Pause/Resume':
                pause(window)
            elif event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                window.close()
                return False
            elif event == 'Back to play-by-play menu':
                window.close()
                return True
        tNow, lineId, action = treat_second(tNow, action, lineId, lines, score, lastQ, window, imageFolder)