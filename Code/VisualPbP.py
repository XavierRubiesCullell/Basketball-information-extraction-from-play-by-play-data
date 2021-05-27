import time
import datetime
import math
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
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

def convert_to_bytes(img, resize=None):
    if isinstance(img, str):
        img = PIL.Image.open(img)
    if resize:
        curWidth, curHeight = img.size
        newWidth, newHeight = resize
        scale = min(newHeight/curHeight, newWidth/curWidth)
        img = img.resize((int(curWidth*scale), int(curHeight*scale)), PIL.Image.ANTIALIAS)
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

def show_action(action, prevAction, home, away, window, imageFolder):
    imageSize = (400, 400)
    if action == "black":
        if window is None:
            print("\n")
        else:
            if prevAction != "black":
                window['ActionText'].update(str(""))
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Black.jpg", resize=imageSize))
    else:
        if window is None:
            print(action.strip().split(", ")[1:], "\n")
        else:
            action = action.strip().split(", ")
            actionType = action[3]
            if actionType == "S":
                team, player, points = action[1], action[2], int(action[4])
                distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
                result = action[5+distGiven] #in/out
                if len(action) == 8+distGiven and action[6+distGiven] == "A": # there is an assist
                    window['ActionText'].update(str(action[1:]))
                    window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=imageSize))
                else:
                    if points == 1:
                        text = f"free throw"
                    else:
                        text = f"{points}-pointer"
                        if distGiven:
                            text += f" from {action[5]} ft"
                    if result == "I":
                        text += " that went in"
                    else:
                        text += " that went out"
                    window['ActionText'].update(text)
                    image = f"{imageFolder}/Shot.png"
                    myImage = PIL.Image.open(image)
                    imageEditable = PIL.ImageDraw.Draw(myImage)
                    print(player)
                    data="UTF-8 data"
                    udata=player.decode("UTF-8")
                    player=udata.encode("latin-1","ignore")
                    imageEditable.text((60,245), player, (0, 0, 0))
                    if team == "1":
                        teamName = home
                    else:
                        teamName = away
                    imageEditable.text((80,265), teamName, (0, 0, 0))
                    # titleFont = PIL.ImageFont.truetype('playfair/playfair-font.ttf', 20)
                    # imageEditable.text((100,15), titleText, (256, 256, 256), font=titleFont)
                    window['ActionImage'].update(data=convert_to_bytes(myImage, resize=imageSize))
            elif actionType == "R":
                window['ActionText'].update(str(action[1:]))
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Rebound.png", resize=imageSize))
            elif actionType == "T":
                window['ActionText'].update(str(action[1:]))
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Bryant.jpg", resize=imageSize))
            elif actionType == "St":
                window['ActionText'].update(str(action[1:]))
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Steal.png", resize=imageSize))
            elif actionType == "B":
                window['ActionText'].update(str(action[1:]))
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Block.png", resize=imageSize))
            elif actionType == "F":
                window['ActionText'].update(str(action[1:]))
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Foul.png", resize=imageSize))
            elif actionType == "C":
                window['ActionText'].update(str(action[1:]))
                window['ActionImage'].update(data=convert_to_bytes(f"{imageFolder}/Change.png", resize=imageSize))


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


def treat_second(tNow, prevAction, lineId, lines, score, home, away, lastQ, window, imageFolder):
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
    time.sleep(t/2)
    if prevAction != "black":
        start = time.time()
        while time.time() - start < 2:
            if window is not None:
                event, _ = window.read(timeout=25)
                if event == 'Pause/Resume':
                    pause(window)
                elif event == sg.WIN_CLOSED:
                    window.close()
                    break

    show_header(tNow, score, window)
    if tNow == clockNext and lineId < nLines:
        action = lines[lineId]
        update_score(action, score)
        lineId += 1
    else:
        action = "black"
    show_action(action, prevAction, home, away, window, imageFolder)
        
    if lineId >= nLines-1 or get_clock(lineId-1, lines) != get_clock(lineId, lines):
        tNow = next_time(tNow)

    return tNow, lineId, action


def main(file, home, away, lastQ, window=None, imageFolder="VisualPbPImages"):
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
        tNow, lineId, action = treat_second(tNow, action, lineId, lines, score, home, away, lastQ, window, imageFolder)