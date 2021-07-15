import time
import datetime
import math
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import io
import PySimpleGUI as sg

from Functions import *


def get_img_data(img, maxsize=(500, 500), first=False):
    """Generate image data using PIL
    """
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return PIL.ImageTk.PhotoImage(img)


def visualPbP_menu(home, away, imageFolder):
    image = PIL.Image.open(f"{imageFolder}/Black.png")
    layout = [
        [ sg.Button("Pause", key='Pause/Resume') ],
        [ sg.Text(key='ActionText', size=(40,1)) ],
        [ sg.Image(data=get_img_data(image, first=True), key='ActionImage') ],
        [ sg.Text("", size=(10,1), key='Clock'),
            sg.Text(home),
            sg.Text("", size=(3,1), key='Score1'),
            sg.Text(away),
            sg.Text("", size=(2,1), key='Score2') ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Visual PbP", layout)


def get_clock(i, lines):
    '''
    This function returns the clock of a play
    - i: play index (integer)
    - lines: list of plays of the match (list of string)
    Output: clock (string)
    '''
    action = lines[i]
    action = action.split(", ")
    return action[0]


def interval(tBefore, tNow):
    '''
    This function computes the length of the sleep interval from a time interval
    - tBefore, tNow: time instants (string)
    Output: sleep length
    '''
    tBefore = time_from_string(tBefore)
    tNow = time_from_string(tNow)
    diff = tBefore - tNow
    diff = diff.seconds
    diff == max(diff, 1)
    return math.exp(-math.pow(diff,2) / (2*math.pow(5,2)))


def next_time(t):
    '''
    This function returns the instant that comes immediately after t
    - t: time instant (string)
    Output: time instant (string)
    '''
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


def show_header(t, score, window):
    '''
    This function updates the values of the clock and the scoreboard
    - t: clock (string)
    - score: current scoreboard values (list of integer)
    - window: window where the plays are shown (PySimpleGUI.PySimpleGUI.Window)
    '''
    if window is None:
        print(t, score, sep="        ")
    else:
        window['Clock'].update(value=t)
        window['Score1'].update(value=score[0])
        window['Score2'].update(value=score[1])


def text_on_image(img, position, text, fontSize):
    img.text(
        xy=position,
        text=text,
        fill=(0, 0, 0),
        font = PIL.ImageFont.truetype("DejaVuSans.ttf", fontSize)
    )


def show_action(action, prevAction, home, away, window, imageFolder):
    '''
    This function updates the play image and the play description
    - action: current play (string)
    - prevAction: previous action (string)
    - home: home team short name (string)
    - away: away team short name (string)
    - window: window where the plays are shown (PySimpleGUI.PySimpleGUI.Window)
    - imageFolder: image directory in case window is True (string)
    '''
    if action == "black":
        if window is None:
            print("\n")
        else:
            if prevAction != "black":
                window['ActionText'].update(str(""))
                image = PIL.Image.open(f"{imageFolder}/Black.png")
                window['ActionImage'].update(data=get_img_data(image, first=True))
    else:
        if window is None:
            print(action.strip().split(", ")[1:], "\n")
        else:
            action = action.strip().split(", ")
            actionType = action[3]


            if actionType == "S": # the play is a shot
                team, player, points = int(action[1]), action[2], int(action[4])
                distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
                result = action[5+distGiven] #in/out
                teamName = (home, away)[team-1]

                if len(action) == 8+distGiven and action[6+distGiven] == "A": # there is an assist
                    image = PIL.Image.open(f"{imageFolder}/AssistedShot.png")
                    imageEditable = PIL.ImageDraw.Draw(image)
                    
                    passer = action[7+distGiven]
                    text = f"{points}-pointer"
                    if distGiven:
                        text += f" from {action[5]} ft"

                    playerPos = (309 - (len(player)-1)*2.5, 285)
                    passerPos = (108 - (len(passer)-1)*2.5, 350)
                    teamPos = (290, 305)
                    opTeamPos = (90, 375)
                    text_on_image(imageEditable, playerPos, player, 7)
                    text_on_image(imageEditable, teamPos, teamName, 15)
                    text_on_image(imageEditable, passerPos, passer, 8)
                    text_on_image(imageEditable, opTeamPos, teamName, 15)

                    window['ActionText'].update(text)
                    window['ActionImage'].update(data=get_img_data(image, first=True))

                else:
                    image = PIL.Image.open(f"{imageFolder}/Shot.png")
                    imageEditable = PIL.ImageDraw.Draw(image)

                    if points == 1:
                        text = "Free throw"
                    else:
                        text = f"{points}-pointer"
                        if distGiven:
                            text += f" from {action[5]} ft"
                    if result == "I":
                        text += " that went in"
                    else:
                        text += " that went out"

                    playerPos = (125 - (len(player)-1)*2.5, 320)
                    teamPos = (110, 355)
                    text_on_image(imageEditable, playerPos, player, 14)
                    text_on_image(imageEditable, teamPos, teamName, 30)

                    window['ActionText'].update(text)
                    window['ActionImage'].update(data=get_img_data(image, first=True))


            elif actionType == "R": # the play is a rebound
                image = PIL.Image.open(f"{imageFolder}/Rebound.png")
                imageEditable = PIL.ImageDraw.Draw(image)

                team, player, kind = int(action[1]), action[2], action[4]
                teamName = (home, away)[team-1]
                if kind == 'O':
                    text = "Offensive"
                else:
                    text = "Defensive"

                playerPos = (275 - (len(player)-1)*2.5, 365)
                teamPos = (270, 395)
                text_on_image(imageEditable, playerPos, player, 12)
                text_on_image(imageEditable, teamPos, teamName, 30)

                window['ActionText'].update(text)
                window['ActionImage'].update(data=get_img_data(image, first=True))


            elif actionType == "T": # the play is a turnover
                image = PIL.Image.open(f"{imageFolder}/Turnover.png")
                imageEditable = PIL.ImageDraw.Draw(image)

                team, player = int(action[1]), action[2]
                teamName = (home, away)[team-1]

                playerPos = (185 - (len(player)-1)*2.5, 112)
                teamPos = (172, 155)
                text_on_image(imageEditable, playerPos, player, 12)
                text_on_image(imageEditable, teamPos, teamName, 23)

                window['ActionText'].update("")
                window['ActionImage'].update(data=get_img_data(image, first=True))


            elif actionType == "St": # the play is a steal
                image = PIL.Image.open(f"{imageFolder}/Steal.png")
                imageEditable = PIL.ImageDraw.Draw(image)

                team, player, opPlayer = int(action[1]), action[2], action[4]
                teamName = (home, away)[team-1]
                opTeam = other_team(team)
                opTeamName = (home, away)[opTeam-1]

                playerPos = (322 - (len(player)-1)*2.5, 205)
                opPlayerPos = (108 - (len(opPlayer)-1)*2.5, 195)
                teamPos = (325, 230)
                opTeamPos = (110, 225)
                text_on_image(imageEditable, playerPos, player, 11)
                text_on_image(imageEditable, teamPos, teamName, 20)
                text_on_image(imageEditable, opPlayerPos, opPlayer, 9)
                text_on_image(imageEditable, opTeamPos, opTeamName, 20)

                window['ActionText'].update("")
                window['ActionImage'].update(data=get_img_data(image, first=True))


            elif actionType == "B": # the play is a block
                image = PIL.Image.open(f"{imageFolder}/Block.png")
                imageEditable = PIL.ImageDraw.Draw(image)

                team, player, opPlayer, points = int(action[1]), action[2], action[4], action[5]
                teamName = (home, away)[team-1]
                opTeam = other_team(team)
                opTeamName = (home, away)[opTeam-1]

                playerPos = (251 - (len(player)-1)*2.5, 330)
                opPlayerPos = (362 - (len(opPlayer)-1)*2.5, 425)
                teamPos = (235, 357)
                opTeamPos = (351, 455)
                text_on_image(imageEditable, playerPos, player, 9)
                text_on_image(imageEditable, teamPos, teamName, 20)
                text_on_image(imageEditable, opPlayerPos, opPlayer, 10)
                text_on_image(imageEditable, opTeamPos, opTeamName, 20)

                text = f"The shot was a {points}-pointer"
                if len(action) == 7:
                    text += f" from {action[5]} ft"

                window['ActionText'].update(text)
                window['ActionImage'].update(data=get_img_data(image, first=True))


            elif actionType == "F": # the play is a foul
                image = PIL.Image.open(f"{imageFolder}/Foul.png")
                imageEditable = PIL.ImageDraw.Draw(image)

                team, player, kind = int(action[1]), action[2], action[4]
                teamName = (home, away)[team-1]
                playerPos = (130 - (len(player)-1)*2.5, 350)
                teamPos = (117, 380)
                text_on_image(imageEditable, playerPos, player, 12)
                text_on_image(imageEditable, teamPos, teamName, 20)
                if len(action) == 6: # there is a player from the opposite team that receives the foul
                    opPlayer = action[5]
                    opTeam = other_team(team)
                    opTeamName = (home, away)[opTeam-1]
                    opPlayerPos = (300 - (len(opPlayer)-1)*2.5, 355)
                    opTeamPos = (287, 385)
                    text_on_image(imageEditable, opPlayerPos, opPlayer, 12)
                    text_on_image(imageEditable, opTeamPos, opTeamName, 20)
                
                if kind == "O":
                    text = "Offensive"
                elif kind == "D":
                    text = "Defensive"
                else:
                    text = "Technical"

                window['ActionText'].update(text)
                window['ActionImage'].update(data=get_img_data(image, first=True))


            elif actionType == "Su": # the play is a substitution
                image = PIL.Image.open(f"{imageFolder}/Substitution.png")
                imageEditable = PIL.ImageDraw.Draw(image)

                team, playerOut, playerIn = int(action[1]), action[2], action[4]
                teamName = (home, away)[team-1]
                outPos = (120 - (len(playerOut)-1)*2.5, 200)
                outTeamPos = (103, 230)
                inPos = (373 - (len(playerIn)-1)*2.5, 225)
                inTeamPos = (359, 255)
                text_on_image(imageEditable, outPos, playerOut, 10)
                text_on_image(imageEditable, outTeamPos, teamName, 20)
                text_on_image(imageEditable, inPos, playerIn, 11)
                text_on_image(imageEditable, inTeamPos, teamName, 20)

                window['ActionText'].update("")
                window['ActionImage'].update(data=get_img_data(image, first=True))



def update_score(line, score):
    '''
    This function updates the current score
    - line: current play (string)
    - score: current scoreboard values (list of integer)
    '''
    action = line.strip().split(", ")
    if len(action) > 3 and action[3] == "S":
        distGiven = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        result = action[5 + distGiven]
        if result == "I": # the shot was in
            team = int(action[1])
            points = int(action[4])
            score[team-1] += points


def pause(window):
    '''
    This function treates the pauses in the match development
    - window: window where the plays are shown (PySimpleGUI.PySimpleGUI.Window)
    '''
    window['Pause/Resume'].update("Resume")
    while True:
        event, _ = window.read()
        if event == 'Pause/Resume':
            window['Pause/Resume'].update("Pause")
            break
        elif event == 'Back':
            global isBack
            isBack = True
            break
        elif event == sg.WIN_CLOSED:
            global isClosed
            isClosed = True
            break


def treat_second(tNow, prevAction, lineId, lines, score, home, away, lastQ, window, imageFolder):
    '''
    - tNow: current time (string)
    - prevAction: previous play (string)
    - lineId: index in lines (integer)
    - lines: list of plays of the match (list of string)
    - score: current scoreboard values (list of integer)
    - home: home team short name (string)
    - away: away team short name (string)
    - lastQ: last quarter of the match (string)
    - window: window where the plays are shown (PySimpleGUI.PySimpleGUI.Window)
    - imageFolder: image directory in case window is True (string)
    Output:
    - tNow: new time (string)
    - lineId: index in lines. It may be the same or increased by 1 in case there was a play at tNow (integer)
    - action: play (string)
    '''
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
                elif event == 'Back':
                    global isBack
                    isBack = True
                    break
                elif event == sg.WIN_CLOSED:
                    global isClosed
                    isClosed = True
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


def main(file, home, away, lastQ, window=False, imageFolder="VisualPbPImages"):
    '''
    This function launches play-by-play
    - file: play-by-play input file (string)
    - home: home team short name (string)
    - away: away team short name (string)
    - lastQ: last quarter of the match (string)
    - window: whether we want a visual support or console printing (bool)
    - imageFolder: image directory in case window is True (string)
    Output: None if the match is finished, True if Back is selected or False if the window is closed
    '''
    os.chdir(os.path.dirname(__file__))
    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    tNow = "1Q:12:00"
    score = [0, 0]
    lineId = 0
    action = "black"

    if window:
        window = visualPbP_menu(home, away, imageFolder="VisualPbPImages")
    else:
        window = None

    global isBack
    isBack = False
    global isClosed
    isClosed = False

    while time_from_string(tNow) >= time_from_string(lastQ+":00:00"):
        if window is not None:
            event, _ = window.read(timeout=25)
            if event == 'Pause/Resume':
                pause(window)
            elif event == 'Back':
                isBack = True
            elif event == sg.WIN_CLOSED:
                isClosed = True

            if isBack:
                window.close()
                return True
            if isClosed:
                return False
        tNow, lineId, action = treat_second(tNow, action, lineId, lines, score, home, away, lastQ, window, imageFolder)