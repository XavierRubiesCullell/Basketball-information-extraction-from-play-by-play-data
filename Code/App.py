import PySimpleGUI as sg
import pandas as pd
import numpy as np
import datetime
import os

from MatchClass import Match


### AUXILIARY FUNCTIONS

def convert_date_match(date):
    '''
    This functions receives a date in format "YYYY/MM/DD" and returns it in format "YYYYMMDD"
    '''
    date = datetime.datetime.strptime(date, "%Y/%m/%d")
    return date.strftime("%Y%m%d")

def convert(name):
    diff = 4 - len(name)
    if diff > 0:
        half = int(diff/2)
        return " "*(diff-half) + name + " "*half
    return name

def create_table(table, indexCol):
    auxTable = table.copy()
    auxTable[indexCol] = auxTable.index
    auxTable = auxTable.rename(convert, axis="columns")
    cols = auxTable.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    return auxTable[cols]


### WINDOW FUNCTIONS

def main_menu():
    buttonSize = (17,1)
    layout = [
        [ sg.Text("Main Menu") ],
        [ sg.Button('Analyse match', size = buttonSize)],
        [ sg.Button('Analyse season', size = buttonSize)]
    ]
    return sg.Window("Main Menu", layout)

def defineMatch_menu():
    buttonSize = (5,1)
    inputSize = (25,1)
    layout = [
        [ sg.Text("Match definition menu") ],
        [ sg.Text("Home", size=buttonSize), sg.Input(key='Home', size=inputSize)],
        [ sg.Text("Away", size=buttonSize), sg.Input(key='Away', size=inputSize)],
        [ sg.Text("Date", size=buttonSize), sg.Input(key='Date', size=(15,1)), sg.CalendarButton(button_text="Calendar", format = "%Y/%m/%d", target='Date', begin_at_sunday_plus=1)],
        [ sg.Button('OK')],
        [ sg.Text("")],
        [ sg.Button('Back to main menu')]
    ]
    return sg.Window("Define Match Menu", layout)

def analyseMatch_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Match analysis menu") ],
        [ sg.Button('Box scores', size = buttonSize)],
        [ sg.Button('Match statistics', size = buttonSize)],
        [ sg.Button('Playing times', size = buttonSize)],
        [ sg.Button('Assists statistics', size = buttonSize)],
        [ sg.Button('Shooting statistics', size = buttonSize)],
        [ sg.Button('See play-by-play', size = buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back to define match menu')]
    ]
    return sg.Window("Analyse Match Menu", layout)

def chooseBoxScore_menu():
    inputSize = (15,1)
    layout = [
        [ sg.Text("Choose the time interval you desire:") ],
        [ sg.Input(key='Start', size=inputSize), sg.Input(key='End', size=inputSize)],
        [ sg.Text("Choose the box score you desire:") ],
        #[ sg.Button('Local'), sg.Button('Visiting'), sg.Button('Both')],
        [ sg.Checkbox("Local", key = 'Local'), sg.Checkbox("Visiting", key = 'Visiting')],
        [ sg.Button('OK')],
        [ sg.Text("")],
        [ sg.Button('Back to analyse match menu')]
    ]
    return sg.Window("Box score election menu", layout)

def analyseBoxScore_menu(table, game):
    auxTable = create_table(table, "Player")
    layout = [
        [sg.Table(values=auxTable.values.tolist(), headings=auxTable.columns.tolist(), num_rows=len(auxTable), alternating_row_color = 'gray', hide_vertical_scroll = True)],
        [sg.Text("Filter:")],
        [sg.Input(key='Filter condition')],
        [
            sg.Radio('Filter by players', "RADIO1", key="Pla"),
            sg.Radio('Filter by categories', "RADIO1", key="Cat"),
            sg.Radio('Filter by value', "RADIO1", key="Val"),
            sg.Button('Filter')
        ],
        [sg.Text("Save:")],
        [
            sg.Text("The box score will be saved in: " + game.home + "_" + game.away + "_" + convert_date_match(game.date) + "_BS_"),
            sg.Input(key='SaveFile', size = (15,1)),
            sg.Text(".csv"),
            sg.Button('Save')
        ],
        [ sg.Text("")],
        [ sg.Button('Back to choose box score menu')]
    ]
    return sg.Window("Box score menu", layout)

def matchStatistics_menu(game):
    table1 = create_table(game.quarter_scorings(), " ")
    layout1 = [
        [sg.Table(values=table1.values.tolist(), headings=table1.columns.tolist(), col_widths = [5]*len(table1.columns), auto_size_columns = False, num_rows=len(table1), hide_vertical_scroll = True, row_height = 20)]
    ]

    table2 = pd.DataFrame(np.array((
        ["Longest drought"]+list(game.longest_drought()),
        ["Greatest partial"]+list(game.greatest_partial()),
        ["Greatest streak"]+list(game.greatest_streak()))
        ), columns = ("Statistic", game.home, game.away))
    layout2 = [
        [sg.Table(values=table2.values.tolist(), headings=table2.columns.tolist(), num_rows=len(table2), hide_vertical_scroll = True, row_height = 20)]
    ]
    
    # indexSize = (12,1)
    # colSize = (6,1)
    # stats = [
    #     ("Longest drought", game.longest_drought()),
    #     ("Greatest partial", game.greatest_partial()),
    #     ("Greatest streak", game.greatest_streak())
    # ]
    # layout2 = [
    #     [
    #         sg.Text("", size=indexSize),
    #         sg.Text(game.home, size=colSize, justification="center"),
    #         sg.Text(game.away, size=colSize, justification="center")
    #     ]
    # ] + [
    #     [
    #         sg.Text(stat[0], size=indexSize),
    #         sg.Text(stat[1][0], size=colSize, justification="right"),
    #         sg.Text(stat[1][1], size=colSize, justification="right")
    #     ]
    #     for stat in stats
    # ]
    layout = [
        [sg.Text("Match Statistics Menu")],
        [sg.Text("Quarter scorings:")],
        layout1,
        [sg.Text("")],
        [sg.Text("Match statistics:")],
        layout2,
        [ sg.Text("")],
        [sg.Button('Back to analyse match menu')]
    ]

    return sg.Window("Match Statistics Menu", layout)

def seePbP_menu():
    buttonSize = (15,1)
    layout = [
        [ sg.Text("Play-by-play Menu") ],
        [ sg.Button('Text mode', size = buttonSize)],
        [ sg.Button('Visual mode', size = buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back to analyse match menu')]
    ]
    return sg.Window("Play-by-play Menu", layout)

def textPbP_menu(game):
    os.chdir(os.path.dirname(__file__))
    with open(game.PbPFile, encoding="utf-8") as f:
        lines = f.readlines()

    cols = ["clock", "team", "player", "action", "action information"]
    plays = pd.DataFrame(columns=cols)
    for line in lines:
        action = line.strip().split(", ")
        row = [action[0], action[1], action[2], action[3], ",".join(action[4:])]
        row = pd.Series(row, index=cols)
        plays = plays.append(row, ignore_index=True)
    layout = [
        [ sg.Text("Text play-by-play Menu") ],
        [sg.Table(values=plays.values.tolist(), headings=cols, justification="left", num_rows=20, row_height=15)],
        [sg.Button('Back to play-by-play menu')]
    ]
    return sg.Window("Text play-by-play Menu", layout)


### INTERACTIVE FUNCTIONS

def analyseBoxScore(game, table):
    window = analyseBoxScore_menu(table, game)
    event, values = window.read()

    window.close()
    try:
        if event == 'Filter':
            print(values['Pla'], values['Cat'], values['Val'])
            if values['Pla']:
                table = game.filter_by_players(table, values['Filter condition'].split(", "))
                analyseBoxScore(game, table)

            elif values['Cat']:
                cats = values['Filter condition']
                print(cats)
                if "," in cats:
                    cats = cats.split(", ")
                table = game.filter_by_categories(table, cats)
                analyseBoxScore(game, table)

            elif values['Val']:
                cats = values['Filter condition']
                auxCats = cats.split(", ")
                auxCats = list(map(lambda x: x.split(": "), auxCats))
                cats = {}
                for cat in auxCats:
                    cats[cat[0]] = int(cat[1])
                table = game.filter_by_value(table, cats)
                analyseBoxScore(game, table)
        
        elif event == 'Save':
            # print(window['hola'])
            game.box_score_save(table, pkl=values['SaveFile'], folder="Files/")
            analyseBoxScore(game, table)
    except:
        sg.popup_error("There was an error in your input. Please check the syntax you need to use")
    if event == 'Back to choose box score menu':
        window.close()
        chooseBoxScore(game)


def chooseBoxScore(game):
    window = chooseBoxScore_menu()
    event, values = window.read()

    if event == 'OK':
        start = values['Start']
        if start == "":
            start = None
        end = values['End']
        if end == "":
            end = None
        if values['Local'] and values['Visiting']:
            table = game.box_scores(start=start, end=end, joint=True)
        else:
            boxScores = game.box_scores(start=start, end=end)
            if values['Local']:
                table = boxScores[0]
            elif values['Visiting']:
                table = boxScores[1]
        window.close()
        analyseBoxScore(game, table)
    elif event == 'Back to analyse match menu':
        window.close()
        analyseMatch(game)


def matchStatistics(game):
    window = matchStatistics_menu(game)
    event, values = window.read()

    if event == 'Back to analyse match menu':
        window.close()
        analyseMatch(game)


def textPbP(game):
    window = textPbP_menu(game)
    event, values = window.read()

    if event == 'Back to play-by-play menu':
        window.close()
        seePbP(game)


def seePbP(game):
    window = seePbP_menu()
    event, values = window.read()

    if event == 'Text mode':
        window.close()
        textPbP(game)

    elif event == 'Back to analyse match menu':
        window.close()
        analyseMatch(game)


def analyseMatch(game):
    window = analyseMatch_menu()
    event, values = window.read()

    if event == 'Box scores':
        window.close()
        chooseBoxScore(game)
    elif event == 'Match statistics':
        window.close()
        matchStatistics(game)
    elif event == 'See play-by-play':
        window.close()
        seePbP(game)
    elif event == 'Back to define match menu':
        window.close()
        defineMatch()


def defineMatch():
    window = defineMatch_menu()
    event, values = window.read()

    if event == 'OK':
        game = Match(values['Home'], values['Away'], values['Date'])
        window.close()
        analyseMatch(game)
    elif event == 'Back to main menu':
        window.close()
        main()


def main():
    window = main_menu()
    event, values = window.read()

    if event == 'Analyse match':
        window.close()
        defineMatch()

if __name__ == '__main__':
    main()