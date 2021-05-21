import os
from bs4 import BeautifulSoup
import urllib.request
import datetime
import re
from Functions import *


def shoot(play, outLine):
    '''
    This function treats a play consisting on a shot
    - play: row of the webpage representing an action (bs4.element.Tag)
    - outLine: line being written to add to the PbP file (string)
    Output: line to be added to the PbP file (list)
    '''
    players = play.find_all("a", href=True)

    if "block" in play.text:
        outLine[1] = str(other_team(int(outLine[1])))
        outLine.append(players[1].text)
        outLine.append('B')
        outLine.append(players[0].text)
        ind = play.text.index("-pt")
        outLine.append(play.text[ind-1])

    else:
        outLine.append(players[0].text)
        outLine.append("S")
        try:
            ind = play.text.index("-pt")
            outLine.append(play.text[ind-1])
            dist = re.search("(\d+)(?!.*\d).+?(?=ft)", play.text)
            try:
                outLine.append(dist.group(1))
            except AttributeError:
                outLine.append("0")
        except ValueError:
            outLine.append("1")

        if "makes" in play.text:
            outLine.append('I')

            if len(players) == 2:
                outLine += ['A', players[1].text]
        else:
            outLine.append('O')

    return outLine


def rebound(play, outLine):
    '''
    This function treats a play consisting on a rebound
    - play: row of the webpage representing an action (bs4.element.Tag)
    - outLine: line being written to add to the PbP file (string)
    Output: line to be added to the PbP file (list)
    '''
    player = play.find("a", href=True)
    if player: # the player is determined (sometimes it is not)
        player = player.text
    else:
        player = '-'
    outLine.append(player)

    outLine.append('R')
    if "Defensive" in play.text:
        outLine.append('D')
    else:
        outLine.append('O')
    return outLine


def turnover(play, outLine):
    '''
    This function treats a play consisting on a turnover
    - play: row of the webpage representing an action (bs4.element.Tag)
    - outLine: line being written to add to the PbP file (string)
    Output: line to be added to the PbP file (list)
    '''
    players = play.find_all("a", href=True)
    if "foul" in play.text: # we do not store the turnover corresponding to an offensive foul, we will compute it anyways
        outLine = []
        return outLine
    if "steal" in play.text: # we store the turnover as a steal
        outLine[1] = str(other_team(int(outLine[1])))
        outLine.append(players[1].text)
        outLine.append("St")
        outLine.append(players[0].text)
        return outLine
    else:
        if len(players) == 1: # the player is determined (sometimes it is not)
            player = players[0].text
        else:
            player = '-'
        
        outLine += [player, "T"]
        return outLine


def foul(play, outLine):
    '''
    This function treats a play consisting on a foul
    - play: row of the webpage representing an action (bs4.element.Tag)
    - outLine: line being written to add to the PbP file (string)
    Output: line to be added to the PbP file (list)
    '''
    players = play.find_all("a", href=True)
    if len(players) > 0: # the player is determined (sometimes it is not)
        player = players[0].text
    else:
        player = '-'
    outLine.append(player)

    outLine.append("F")
    if "Offensive" in play.text:
        outLine.append("O")
    else:
        if "Loose ball" in play.text:
            pass
        else:
            outLine[1] = str(other_team(int(outLine[1])))
        outLine.append("D")

    if len(players) == 2:
        outLine.append(players[1].text)
    return outLine


def change(play, outLine):
    '''
    This function treats a play consisting on a change
    - play: row of the webpage representing an action (bs4.element.Tag)
    - outLine: line being written to add to the PbP file (string)
    Output: line to be added to the PbP file (list)
    '''
    players = play.find_all("a", href=True)
    playerOut = players[1].text
    playerIn = players[0].text
    outLine += [playerOut, "C", playerIn]
    return outLine


def treat_play(play, outLine):
    '''
    This function treats a play information and classifies it
    - play: row of the webpage representing an action (bs4.element.Tag)
    - outLine: line being written to add to the PbP file (string)
    Output: line to be added to the PbP file (list)
    '''
    if "makes" in play.text or "misses" in play.text:
        outLine = shoot(play, outLine)
    elif "rebound" in play.text:
        outLine = rebound(play, outLine)
    elif "Turnover" in play.text or "Violation" in play.text:
        outLine = turnover(play, outLine)
    elif "foul" in play.text:
        outLine = foul(play, outLine)
    elif "enters" in play.text:
        outLine = change(play, outLine)
    elif "timeout" in play.text:
        outLine += ["- ", "Timeout"]
    elif "Replay" in play.text:
        outLine += ["-", "Instant Replay"]
    else:
        outLine.append("NOT TREATED")
    return outLine


def treat_action(action, Q):
    '''
    This function treats an action and classifies it
    - action: row of the webpage representing an action (bs4.element.Tag)
    - Q: current quarter (string)
    '''
    outLine = []

    cols = action.find_all('td')
    clock = cols[0].text
    clock = datetime.datetime.strptime(clock, "%M:%S.%f")
    clock = clock.strftime("%M:%S")
    outLine.append(Q + ":" + clock)

    if len(cols[1].text) > 1: # the action belongs to the visiting team
        outLine.append("2")
        play = cols[1]
    else:
        outLine.append("1") # the action belongs to the local team
        play = cols[5]

    outLine = treat_play(play, outLine)
    if len(outLine) != 0:
        actions.append(outLine)


def treat_line(row, Q, prevClock):
    '''
    This function treats a line and recognises if it is a game action. If so, it launches treat_action
    - row: row of the webpage (bs4.element.Tag)
    - Q: current quarter (string)
    - prevClock: timestamp of the previous action (string)
    Ouput:
    - Q: current quarter (string)
    - clock: timestamp of the action (string)
    '''
    cols = row.find_all('td')
    if len(cols) == 0: # this is not an action, it is a header
        nonActions.append(row)
        clock = prevClock # as this function returns clock, but this line does not have it, we return the previous value

    else:
        clock = row.find('td').text
        if len(cols) == 2: # this is a neutral action, such as a jump ball or a quarter start/end
            if prevClock == "0:00.0" and clock != prevClock:
                Q = next_quarter(Q)
            neutralActions.append(row)

        else:
            treat_action(row, Q)

    return Q, clock


def print_results():
    '''
    This function prints the classification of the lines of the PbP file
    '''
    print("Actions", len(actions))
    for el in actions:
        print(el)
    print("\nNon actions", len(nonActions))
    for el in nonActions:
        print(el)
    print("\nNeutral actions", len(neutralActions))
    for el in neutralActions:
        print(el)


def main(webpage, outFile):
    '''
    This function creates the standard PbP file
    - webpage: link of the webpage where the information must be fetched (string)
    - outFile: path of the file where the standard PbP will be stored (string)
    Ouput: last quarter of the match (string)
    '''
    os.chdir(os.path.dirname(__file__))

    global actions
    actions = []
    global neutralActions
    neutralActions = []
    global nonActions
    nonActions = []
    Q = "1Q"
    clock = "12:00.0"

    response = urllib.request.urlopen(webpage)
    htmlDoc = response.read()
    soup = BeautifulSoup(htmlDoc, 'html.parser')
    res = soup.find_all('tr')
    
    for line in res:
        Q, clock = treat_line(line, Q, clock)

    #print_results()    

    with open(outFile, "w", encoding="utf8") as out:
        for action in actions:
            out.write(", ".join(action) + '\n')

    return Q