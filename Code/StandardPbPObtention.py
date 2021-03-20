import os
from bs4 import BeautifulSoup
import urllib.request
import datetime
import re

def shoot(play, out_line):
    players = play.find_all("a", href=True)

    if "block" in play.text:
        out_line[1] = str((int(out_line[1])*5)%3)
        out_line.append(players[1].text)
        out_line.append('B')
        out_line.append(players[0].text)
        ind = play.text.index("-pt")
        out_line.append(play.text[ind-1])

    else:
        out_line.append(players[0].text)
        out_line.append("S")
        try:
            ind = play.text.index("-pt")
            out_line.append(play.text[ind-1])
            dist = re.search("(\d+)(?!.*\d).+?(?=ft)", play.text)
            try:
                out_line.append(dist.group(1))
            except AttributeError:
                pass
        except ValueError:
            out_line.append("1")

        if "makes" in play.text:
            out_line.append('I')

            if len(players) == 2:
                out_line += ['A', players[1].text]
        else:
            out_line.append('O')

    return out_line


def rebound(play, out_line):
    player = play.find("a", href=True)
    if player:
        player = player.text
    else:
        player = '-'
    out_line.append(player)

    out_line.append('R')
    if "Defensive" in play.text:
        out_line.append('D')
    else:
        out_line.append('O')
    return out_line


def turnover(play, out_line):
    players = play.find_all("a", href=True)
    if "foul" in play.text:
        out_line = []
        return out_line
    if "steal" in play.text:
        out_line[1] = str((int(out_line[1])*5)%3)
        out_line.append(players[1].text)
        out_line.append("St")
        out_line.append(players[0].text)
        return out_line
    else:
        if len(players) == 1:
            player = players[0].text
        else:
            player = '-'
        
        out_line += [player, "T"]
        return out_line


def foul(play, out_line):
    players = play.find_all("a", href=True)
    if len(players) == 2:
        player = players[0].text
    else:
        player = '-'
    out_line.append(player)

    out_line.append("F")
    if "Offensive" in play.text:
        out_line.append("O")
    else:
        if "Loose ball" in play.text:
            pass
        else:
            out_line[1] = str((int(out_line[1])*5)%3)
        out_line.append("D")

    if len(players) == 2:
        out_line.append(players[1].text)
    return out_line


def change(play, out_line):
    players = play.find_all("a", href=True)
    playerOut = players[1].text
    playerIn = players[0].text
    out_line += [playerOut, "C", playerIn]
    return out_line


def treat_play(play, out_line):
    if "makes" in play.text or "misses" in play.text:
        out_line = shoot(play, out_line)
    elif "rebound" in play.text:
        out_line = rebound(play, out_line)
    elif "Turnover" in play.text:
        out_line = turnover(play, out_line)
    elif "foul" in play.text:
        out_line = foul(play, out_line)
    elif "enters" in play.text:
        out_line = change(play, out_line)
    elif "timeout" in play.text:
        out_line.append("Timeout")
    elif "Replay" in play.text:
        out_line.append("Instant Replay")
    else:
        out_line.append("NOT TREATED")
    return out_line


def treat_action(action, Q):
    out_line = []

    cols = action.find_all('td')
    clock = cols[0].text
    clock = datetime.datetime.strptime(clock, "%M:%S.%f")
    quarter_time = datetime.timedelta(minutes = 12*(4-Q))
    clock = clock + quarter_time
    out_line.append(clock.strftime("%M:%S"))

    if len(cols[1].text) > 1:
        out_line.append("2")
        play = cols[1]
    else:
        out_line.append("1")
        play = cols[5]

    out_line = treat_play(play, out_line)
    if len(out_line) != 0:
        actions.append(out_line)

    return


def treat_line(row, Q):
    cols = row.find_all('td')
    if len(cols) == 0:
        non_actions.append(row)

    elif len(cols) == 2:
        clock = row.find('td').text
        if clock == "12:00.0":
            Q = Q + 1
        neutral_actions.append(row)

    else:
        treat_action(row, Q)

    return Q


def print_results():
    print("Actions", len(actions))
    for el in actions:
        print(el)
    print("\nNon actions", len(non_actions))
    for el in non_actions:
        print(el)
        print()
    print("\nNeutral actions", len(neutral_actions))
    for el in neutral_actions:
        print(el)
        print()


def StandardPbPObtentionMain(webpage, out_file):
    os.chdir(os.path.dirname(__file__))

    global actions
    actions = []
    global neutral_actions
    neutral_actions = []
    global non_actions
    non_actions = []
    Q = 0

    response = urllib.request.urlopen(webpage)
    html_doc = response.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    res = soup.find_all('tr')
    
    for line in res:
        Q = treat_line(line, Q)

    #print_results()    

    with open("Files/" + out_file, "w", encoding="utf8") as out:
        for action in actions:
            out.write(", ".join(action) + '\n')