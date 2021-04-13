import os
from bs4 import BeautifulSoup
import urllib.request
import datetime
import re
from Functions import *


def shoot(play, outLine):
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
                pass
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
    player = play.find("a", href=True)
    if player:
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
    players = play.find_all("a", href=True)
    if "foul" in play.text:
        outLine = []
        return outLine
    if "steal" in play.text:
        outLine[1] = str(other_team(int(outLine[1])))
        outLine.append(players[1].text)
        outLine.append("St")
        outLine.append(players[0].text)
        return outLine
    else:
        if len(players) == 1:
            player = players[0].text
        else:
            player = '-'
        
        outLine += [player, "T"]
        return outLine


def foul(play, outLine):
    players = play.find_all("a", href=True)
    if len(players) == 2:
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
    players = play.find_all("a", href=True)
    playerOut = players[1].text
    playerIn = players[0].text
    outLine += [playerOut, "C", playerIn]
    return outLine


def treat_play(play, outLine):
    if "makes" in play.text or "misses" in play.text:
        outLine = shoot(play, outLine)
    elif "rebound" in play.text:
        outLine = rebound(play, outLine)
    elif "Turnover" in play.text:
        outLine = turnover(play, outLine)
    elif "foul" in play.text:
        outLine = foul(play, outLine)
    elif "enters" in play.text:
        outLine = change(play, outLine)
    elif "timeout" in play.text:
        outLine.append("Timeout")
    elif "Replay" in play.text:
        outLine.append("Instant Replay")
    else:
        outLine.append("NOT TREATED")
    return outLine


def treat_action(action, Q):
    outLine = []

    cols = action.find_all('td')
    clock = cols[0].text
    clock = datetime.datetime.strptime(clock, "%M:%S.%f")
    quarterTime = datetime.timedelta(minutes = 12*(4-Q))
    clock = clock + quarterTime
    outLine.append(clock.strftime("%M:%S"))

    if len(cols[1].text) > 1:
        outLine.append("2")
        play = cols[1]
    else:
        outLine.append("1")
        play = cols[5]

    outLine = treat_play(play, outLine)
    if len(outLine) != 0:
        actions.append(outLine)

    return


def treat_line(row, Q):
    cols = row.find_all('td')
    if len(cols) == 0:
        nonActions.append(row)

    elif len(cols) == 2:
        clock = row.find('td').text
        if clock == "12:00.0":
            Q = Q + 1
        neutralActions.append(row)

    else:
        treat_action(row, Q)

    return Q


def print_results():
    print("Actions", len(actions))
    for el in actions:
        print(el)
    print("\nNon actions", len(nonActions))
    for el in nonActions:
        print(el)
        print()
    print("\nNeutral actions", len(neutralActions))
    for el in neutralActions:
        print(el)
        print()


def main(webpage, outFile):
    os.chdir(os.path.dirname(__file__))

    global actions
    actions = []
    global neutralActions
    neutralActions = []
    global nonActions
    nonActions = []
    Q = 0

    response = urllib.request.urlopen(webpage)
    htmlDoc = response.read()
    soup = BeautifulSoup(htmlDoc, 'html.parser')
    res = soup.find_all('tr')
    
    for line in res:
        Q = treat_line(line, Q)

    #print_results()    

    with open(outFile, "w", encoding="utf8") as out:
        for action in actions:
            out.write(", ".join(action) + '\n')