import PySimpleGUI as sg
import pandas as pd
import numpy as np
import datetime

from MatchClass import Match
from SeasonClass import Season
from Functions import get_team


# AUXILIARY FUNCTIONS

def convert_date_match(date):
    '''
    This functions receives a date in format "YYYY/MM/DD" and returns it in format "YYYYMMDD"
    '''
    date = datetime.datetime.strptime(date, "%Y/%m/%d")
    return date.strftime("%Y%m%d")

def convert(name, size):
    diff = size - len(name)
    if diff > 0:
        half = int(diff/2)
        return " "*(diff-half) + name + " "*half
    return name

def create_table(table, indexCol, size):
    auxTable = table.copy()
    auxTable[indexCol] = auxTable.index
    auxTable.columns = [convert(x, size) for x in auxTable.columns]
    cols = auxTable.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    return auxTable[cols]

# ----------------------------------------------------------------------------------
# WINDOW FUNCTIONS
def main_menu():
    buttonSize = (17,1)
    layout = [
        [ sg.Text("Main Menu") ],
        [ sg.Button('Analyse match', size = buttonSize)],
        [ sg.Button('Analyse season', size = buttonSize)]
    ]
    return sg.Window("Main Menu", layout)

## 1. Analyse match
def defineMatch_menu():
    buttonSize = (5,1)
    inputSize = (25,1)
    layout = [
        [ sg.Text("Match definition menu") ],
        [ sg.Text("Home", size=buttonSize), sg.Input(key='Home', size=inputSize, tooltip="You can write the location, the club name, both or the abbreviation\nFor example: Denver, Nuggets, Denver Nuggets or DEN")],
        [ sg.Text("Away", size=buttonSize), sg.Input(key='Away', size=inputSize, tooltip="You can write the location, the club name, both or the abbreviation\nFor example: Denver, Nuggets, Denver Nuggets or DEN")],
        [ sg.Text("Date", size=buttonSize), sg.Input(key='Date', size=(15,1), tooltip="Use the ISO standard: YYYY/MM/DD"), sg.CalendarButton(button_text="Calendar", format = "%Y/%m/%d", target='Date', begin_at_sunday_plus=1)],
        [ sg.Button('OK', size=buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back', size=buttonSize)]
    ]
    return sg.Window("Define Match Menu", layout)

def analyseMatch_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Match analysis menu") ],
        [ sg.Button('Box scores', size = buttonSize)],
        [ sg.Button('Match statistics', size = buttonSize)],
        [ sg.Button('Playing times', size = buttonSize)],
        [ sg.Button('Shooting statistics', size = buttonSize)],
        [ sg.Button('Assist statistics', size = buttonSize)],
        [ sg.Button('See play-by-play', size = buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back')]
    ]
    return sg.Window("Analyse Match Menu", layout)

### 1.1. Box score
def matchChooseBoxScore_menu():
    buttonSize = (5,1)
    inputSize = (15,1)
    layout = [
        [ sg.Text("Choose the time interval you desire:") ],
        [ sg.Input(key='Start', size=inputSize, tooltip="Introduce the time in format quarter:MM:SS\nquarter can be '1Q','2Q','3Q','4Q','xOT\nIf nothing is written, the beginning of the match will be considered"),
         sg.Input(key='End', size=inputSize, tooltip="Introduce the time in format quarter:MM:SS\nquarter can be '1Q','2Q','3Q','4Q','xOT\nIf nothing is written, the end of the match will be considered")],
        [ sg.Text("Choose the box score you desire:") ],
        [ sg.Checkbox("Local", default = True, key = 'Local'), sg.Checkbox("Visiting", default = True, key = 'Visiting')],
        [ sg.Button('OK', size=buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back', size=buttonSize)]
    ]
    return sg.Window("Box score election menu", layout)

def helpAnalyseBoxScore_menu(cols):
    textSize = (9, 1)
    explanation = {
        "GP": "Games played",
        "2PtM": "2-point shots made",
        "2PtA": "2-point shots attempted",
        "2Pt%": "2-point shots percentage",
        "3PtM": "3-point shots made",
        "3PtA": "3-point shots attempted",
        "3Pt%": "3-point shots percentage",
        "FGM": "field goals made",
        "FGA": "field goals attempted",
        "FG%": "field goals percentage",
        "FTM": "free throws made",
        "FTA": "free throws attempted",
        "FT%": "free throws percentage",
        "OR": "offensive rebounds",
        "DR": "deffensive rebounds",
        "TR": "total rebounds",
        "Ast": "assist",
        "PtsC": "points contribution (points by the player + points after an assist by the player)",
        "Bl": "blocks",
        "St": "steals",
        "To": "turnovers",
        "PF": "personal fouls",
        "DF": "drawn fouls",
        "AstPts": "assisted points",
        "Pts": "points",
        "+/-": "plusminus",
        "PIR": "Performance Index Rating"
    }
    if cols[1] == 'Mins':
        del cols[1]
    if cols[0] == 'Team' or cols[0] == 'Mins':
        del cols[0]
    layout = [
        [sg.Text(cat, size=textSize), sg.Text(explanation[cat])] for cat in cols
    ]
    return sg.Window("Help Menu", layout)

def analyseBoxScore_menu(Event, table):
    try:
        Event.home
        savingText = "The box score will be saved in: " + Event.home + "_" + Event.away + "_" + convert_date_match(Event.date) + "_BS_"
    except:
        savingText = "The box score will be saved in: " + Event.team + "_" + Event.season + "_BS_"
    auxTable = create_table(table, "Player", 4)
    indentation = (1,1)
    layout = [
        [ sg.Button('Help') ],
        [ sg.Table(values=auxTable.values.tolist(), 
            headings=auxTable.columns.tolist(), 
            num_rows=len(auxTable), 
            alternating_row_color = 'gray', 
            hide_vertical_scroll = True) ],
        [ sg.Text("Filter:") ],
        [ sg.Text("", size=indentation), 
            sg.Button('Filter by players'), 
            sg.Button('Filter by categories'), 
            sg.Button('Filter by values'), 
            sg.Button('Get top players') ],
        [ sg.Text("Save:") ],
        [
            sg.Text("", size=indentation),
            sg.Text(savingText),
            sg.Input(key='SaveFile', size = (15,1)),
            sg.Text(".html"),
            sg.Button('Save')
        ],
        [ sg.Button('Back')]
    ]
    return sg.Window("Box score menu", layout)

def filterByPlayers_menu(table):
    layout = [
        [ sg.Text("List of players") ],
        [ sg.Input(key='Filter condition', tooltip="Format: player1, player2, player3, ..."), sg.Button('Filter') ]
    ]
    return sg.Window("Filter by players Menu", layout)

def filterByCategories_menu(table):
    layout = [
        [ sg.Text("List of categories") ],
        [ sg.Input(key='Filter condition', tooltip="Format: category1, category2, category3, ..."), sg.Button('Filter') ]
    ]
    return sg.Window("Filter by categories Menu", layout)

def filterByValues_menu(table):
    layout = [
        [ sg.Text("List of categories and their corresponding values") ],
        [ sg.Input(key='Filter condition', tooltip="Format: category1: value1, category2: value2, category3: value3, ..."), sg.Button('Filter') ]
    ]
    return sg.Window("Filter by values Menu", layout)

def filterByTop_menu(table):
    layout = [
        [ sg.Text("Returns the n players with the maximum/minimum values in the introduced categories") ],
        [ sg.Text("List of categories"),
        sg.Input(key='Filter condition', tooltip="Format: category1, category2, category3, ..."),
        sg.Text("  n"),
        sg.Input(key='n', size=(3,1)),
        sg.Text(" "),
        sg.Combo(("maximum","minimum"), default_value="maximum", readonly=True, tooltip="whether the lowest or the highest values are desired", key='Condition'),
        sg.Button('Filter') ]
    ]
    return sg.Window("Filter top players Menu", layout)

### 1.2. Match statistics
def matchStatistics_menu(game, timestamp):
    if timestamp == "":
        timestamp = None
        header1 = f"Quarter scorings:"
        header2 = "Statistics (maximum values along the match):"
    else:
        header1 = f"Quarter scorings (until {timestamp}):"
        header2 = f"Statistics (values at {timestamp}):"
    table1 = create_table(game.quarter_scorings(timestamp), " ", 4)
    layout1 = [
        [ sg.Table(values=table1.values.tolist(),
        headings = table1.columns.tolist(),
        col_widths = [5]*len(table1.columns),
        auto_size_columns = False,
        num_rows=len(table1),
        hide_vertical_scroll = True,
        row_height = 20,
        key = 'Table1') ]
    ]

    table2 = create_table(game.match_statistics(timestamp), "Statistic", 4)
    layout2 = [
        [ sg.Table(values=table2.values.tolist(),
        headings=table2.columns.tolist(), 
        num_rows=len(table2), 
        hide_vertical_scroll = True, 
        row_height = 20, 
        key = 'Table2') ]
    ]
    
    layout = [
        [ sg.Text("Time"), 
            sg.Input(size=(10,1), 
                tooltip="Introduce the time in format quarter:MM:SS\nquarter can be '1Q','2Q','3Q','4Q','xOT\nIf no time is introduced, maximum values are given", 
                key='Time'), 
            sg.Button('OK') ],
        [ sg.Text("") ],
        [ sg.Text(header1) ],
        layout1,
        [ sg.Text("") ],
        [ sg.Text(header2) ],
        layout2,
        [ sg.Text("")],
        [ sg.Button('Back') ]
    ]

    return sg.Window("Match Statistics Menu", layout)

### 1.3. Playing times
def playingTimes_menu(game):
    teamSize = (25,1)
    textLength = 80
    layout = [
        [ sg.Text("Playing times Menu")],
        [ sg.Text("Five on court at a determined time:")],
        [ sg.Input(size=(10,1), tooltip="Introduce the time in format quarter:MM:SS\nquarter can be '1Q','2Q','3Q','4Q','xOT", key='Time input'), sg.Button("OK", key="Time OK") ],
        [ sg.Text("", size=(5,2), key='Team 1'), sg.Text("", size=(textLength,2), key='Time output 1')],
        [ sg.Text("", size=(5,2), key='Team 2'), sg.Text("", size=(textLength,2), key='Time output 2')],
        [ sg.Text("")],
        [ sg.Text("Intervals of time for a player:")],
        [   sg.Text("Team:"),
            sg.Input(size=teamSize, key='Team player input', tooltip="You can write the location, the club name, both or the abbreviation\nFor example: Denver, Nuggets, Denver Nuggets or DEN"),
            sg.Text("Player:"),
            sg.Input(key='Player input', tooltip="Introduce the initial of the name, a dot and the surname\nExample: L. James", size=(20,1)),
            sg.Button("OK", key="Player OK") ],
        [ sg.Text("", size=(textLength,2), key='Player output')],
        [ sg.Text("")],
        [ sg.Text("Intervals of time for a five:")],
        [   sg.Text("Team:"),
            sg.Input(size=teamSize, key='Team five input', tooltip="You can write the location, the club name, both or the abbreviation\nFor example: Denver, Nuggets, Denver Nuggets or DEN"),
            sg.Text("Five:"),
            sg.Input(key='Five input', tooltip="Introduce the players separed by a comma\nExample: L. James, K. Leonard, S. Curry, J. Harden, C. Paul",size=(60,1)),
            sg.Button("OK", key="Five OK") ],
        [ sg.Text("", size=(textLength,1), key='Five output')],
        [ sg.Text("")],
        [ sg.Button('Back')]
    ]
    return sg.Window("Playing Times Menu", layout)

### 1.4. Shooting statistics
def teamElection_menu():
    radioSize = (10,1)
    layout = [
        [ sg.Radio("Local", "RADIO1", size=radioSize, key='Local') ],
        [ sg.Radio("Visiting", "RADIO1", size=radioSize, key='Visiting') ],
        [ sg.Button('OK') ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Team election Menu", layout)

def shootingStatisticsTable_menu(game, table):
    layout = [
        [ sg.Button('Save') ],
        [ sg.Table(values=table.values.tolist(), 
        headings=table.columns.tolist(),
        num_rows=min(len(table), 30),
        hide_vertical_scroll = len(table) < 30) ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Shooting statistics table Menu", layout)

def statisticsPlot_menu():
    layout = [
        [ sg.Text("Statistics plot Menu") ],
        [ sg.Button('Show plot') ],
        [ sg.Button('Save plot') ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Statistics plot Menu", layout)

def shootingStatisticsMatch_menu():
    buttonSize = (25,1)
    layout = [
        [ sg.Text("Shooting statistics Menu") ],
        [ sg.Radio("Local", "RADIO1", default=True, key='Local') ],
        [ sg.Radio("Visiting", "RADIO1", key='Visiting') ],
        [ sg.Text("") ],
        [ sg.Button('Shooting statistics table', size=buttonSize) ],
        [ sg.Button('Shooting statistics plot', size=buttonSize) ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Shooting statistics Menu", layout)

def shootingStatisticsSeason_menu():
    buttonSize = (25,1)
    layout = [
        [ sg.Text("Shooting statistics Menu") ],
        [ sg.Radio("Own team", "RADIO1", default=True, key='Local') ],
        [ sg.Radio("Opponents", "RADIO1", key='Visiting') ],
        [ sg.Text("") ],
        [ sg.Button('Shooting statistics table', size=buttonSize) ],
        [ sg.Button('Shooting statistics plot', size=buttonSize) ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Shooting statistics Menu", layout)

### 1.5. Assist statistics
def assistStatisticsMatrix_menu(game, team):
    table = game.get_assist_matrix(team)
    table = create_table(table, " ", 4)
    layout = [
        [ sg.Button('Save') ],
        [ sg.Table(values=table.values.tolist(), headings=table.columns.tolist(), num_rows=len(table), hide_vertical_scroll = True) ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Assist statistics matrix Menu", layout)

def assistStatistics_menu():
    buttonSize = (25,1)
    layout = [
        [ sg.Text("Assist statistics Menu") ],
        [ sg.Radio("Local", "RADIO1", default=True, key='Local') ],
        [ sg.Radio("Visiting", "RADIO1", key='Visiting') ],
        [ sg.Text("") ],
        [ sg.Button('Assist statistics matrix', size=buttonSize) ],
        [ sg.Button('Assist statistics plot', size=buttonSize) ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Assist statistics Menu", layout)

### 1.6. PbP
def seePbP_menu():
    buttonSize = (15,1)
    layout = [
        [ sg.Text("Play-by-play Menu") ],
        [ sg.Button('Text mode', size = buttonSize)],
        [ sg.Button('Visual mode', size = buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back')]
    ]
    return sg.Window("Play-by-play Menu", layout)

def helpTextPbP_menu():
    textSize = (20, 1)
    layout = [
        [ sg.Text("S, 2, 5, O:", size=textSize), sg.Text("2-point shot from 5ft that went out") ],
        [ sg.Text("S, 2, 5, I, A, N. Surname:", size=textSize), sg.Text("2-point shot from 5ft that went in, assisted by N. Surname") ],
        [ sg.Text("R, O/D:", size=textSize), sg.Text("Offensive/Deffensive rebound") ],
        [ sg.Text("T:", size=textSize), sg.Text("Turnover") ],
        [ sg.Text("St, N. Surname:", size=textSize), sg.Text("Steal, the ball was stolen from N. Surname") ],
        [ sg.Text("B, N. Surname:", size=textSize), sg.Text("Block, N. Surname was its receiver") ],
        [ sg.Text("F, N. Surname:", size=textSize), sg.Text("Foul, drawn by N. Surname") ],
        [ sg.Text("Su, N. Surname:", size=textSize), sg.Text("Substitution, N. Surname is the player entering the game") ]
    ]
    return sg.Window("Help Menu", layout)

def textPbP_menu(game):
    with open(game.PbPFile, encoding="utf-8") as f:
        lines = f.readlines()

    cols = ["clock", "team", "player", "action", "action information"]
    plays = pd.DataFrame(columns=cols)
    for line in lines:
        action = line.strip().split(", ")
        row = [action[0], action[1], action[2], action[3], ", ".join(action[4:])]
        row = pd.Series(row, index=cols)
        plays = plays.append(row, ignore_index=True)
    layout = [
        [ sg.Text("Text play-by-play Menu", size=(66,1)), sg.Button('Help') ],
        [ sg.Table(values=plays.values.tolist(), headings=cols, justification="left", num_rows=20, row_height=20) ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Text play-by-play Menu", layout)


## 2. Analyse season
def defineSeason_menu():
    buttonSize = (5,1)
    textSize = (7,1)
    inputSize = (25,1)
    layout = [
        [ sg.Text("Season definition menu") ],
        [ sg.Text("Team", size=textSize), sg.Input(key='Team', size=inputSize, tooltip="You can write the location, the club name, both or the abbreviation\nFor example: Denver, Nuggets, Denver Nuggets or DEN") ],
        [ sg.Text("Season", size=textSize), sg.Input(key='Season', size=inputSize, tooltip="Indicate the season in format YYYY-YYYY") ],
        [ sg.Button('OK', size=buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back', size=buttonSize)]
    ]
    return sg.Window("Define Season Menu", layout)

def analyseSeason_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Season analysis menu") ],
        [ sg.Button('See calendar', size = buttonSize) ],
        [ sg.Button('See results', size = buttonSize) ],
        [ sg.Button('Box score', size = buttonSize) ],
        [ sg.Button('Statistic evolution', size = buttonSize) ],
        [ sg.Button('Shooting statistics', size = buttonSize) ],
        [ sg.Button('Assist statistics', size = buttonSize) ],
        [ sg.Text("")],
        [ sg.Text("*Please take into consideration that some calculations might be slow")],
        [ sg.Text("")],
        [ sg.Button('Back')]
    ]
    return sg.Window("Analyse Season Menu", layout)

def calendar_menu(season):
    auxTable = create_table(season.matchTable, " ", 5)
    layout = [
        [ sg.Button('Save') ],
        [   sg.Table(values=auxTable.values.tolist(),
            headings=auxTable.columns.tolist(),
            row_height = 20, 
            num_rows = 15, 
            alternating_row_color = 'gray') ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Calendar Menu", layout)

def results_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Results analysis menu") ],
        [ sg.Button('See results table', size = buttonSize) ],
        [ sg.Button('Results plot', size = buttonSize) ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Statistic Analysis Menu", layout)

def resultsTable_menu(season):
    record = season.record()
    auxTable = create_table(season.get_results_table(), " ", 5)
    layout = [
        [ sg.Text("W - L: "), sg.Text(f"{record[0]} - {record[1]}") ],
        [ sg.Button('Save') ],
        [   sg.Table(values=auxTable.values.tolist(),
            headings=auxTable.columns.tolist(),
            row_height = 20, 
            num_rows = 15, 
            alternating_row_color = 'gray') ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Results table Menu", layout)

def resultsPlot_menu():
    layout = [
        [ sg.Text("Results plot menu") ],
        [ sg.Combo(("Team","Opponent team", "Both", "Difference"), default_value="Team", readonly=True, key='Condition') ],
        [ sg.Button('Show plot') ],
        [ sg.Button('Save plot') ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Results plot Menu", layout)

def seasonChooseBoxScore_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Choose the box score you desire:") ],
        [ sg.Button('Total values', size=buttonSize)],
        [ sg.Button('Per game values', size=buttonSize)],
        [ sg.Button('Per 36 minutes values', size=buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back', size=(5,1))]
    ]
    return sg.Window("Box score election menu", layout)

def statisticElection_menu():
    buttonSize = (5,1)
    radioSize = (13,1)
    layout = [
        [ sg.Text("Statistic election menu") ],
        [ sg.Radio('Greatest difference', "RADIO1", size=radioSize, key='Difference') ],
        [ sg.Radio('Greatest streak', "RADIO1", size=radioSize, key='Streak') ],
        [ sg.Radio('Greatest partial', "RADIO1", size=radioSize, key='Partial') ],
        [ sg.Radio('Longest drought', "RADIO1", size=radioSize, key='Drought') ],
        [ sg.Radio('Box score', "RADIO1", size=radioSize, key='BS'),
            sg.Text("Category"),
            sg.Input(key='Category', size=(7,1)),
            sg.Text("Player"),
            sg.Input(key='Player', size=(20,1), tooltip="Introduce the initial of the name, a dot and the surname\nExample: L. James\nIf no input is given, team value is considered") ],
        [ sg.Button('OK', size=buttonSize) ],
        [ sg.Text("*Box score is slow (takes about 1 minute) and program may warn it is not answering, but just let it work") ],
        [ sg.Text("") ],
        [ sg.Button('Back', size=buttonSize) ]
    ]
    return sg.Window("Statistic Evolution Menu", layout)

def statisticAnalysis_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Statistic analysis menu") ],
        [ sg.Button('See table', size = buttonSize) ],
        [ sg.Button('Show plot', size = buttonSize) ],
        [ sg.Button('Save plot', size = buttonSize) ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Statistic Analysis Menu", layout)

def statisticTable_menu(season, table, statistic):
    auxTable = create_table(table, "Match", 4)
    layout = [
        [ sg.Button('Save') ],
        [   sg.Table(values=auxTable.values.tolist(),
            headings=auxTable.columns.tolist(),
            alternating_row_color = 'gray') ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Statistic Table Menu", layout)

def assistStatisticsMatrixSeason_menu(matrix):
    auxTable = create_table(matrix, " ", 5)
    layout = [
        [ sg.Button('Save') ],
        [   sg.Table(values=auxTable.values.tolist(),
            headings=auxTable.columns.tolist(),
            num_rows=len(auxTable), 
            alternating_row_color = 'gray') ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Assist statistics table Menu", layout)


def assistStatisticsSeason_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Assist statistics menu") ],
        [ sg.Button('See table', size = buttonSize) ],
        [ sg.Button('Show plot', size = buttonSize) ],
        [ sg.Button('Save plot', size = buttonSize) ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Assist statistics Menu", layout)

# ----------------------------------------------------------------------------------
# INTERACTIVE FUNCTIONS

### 1.1. Box score
def matchFilterByPlayers(game, table, BSWindow):
    filterWindow = filterByPlayers_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        players = values['Filter condition']
        players = players.split(", ")

        newTable = game.filter_by_players(table, players)
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, table)
        else:
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        matchAnalyseBoxScore(game, table)


def matchFilterByCategories(game, table, BSWindow):
    filterWindow = filterByCategories_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        if not (isinstance(cats,str) and cats in ("simple", "shooting", "rebounding")):
            cats = cats.split(", ")

        newTable = game.filter_by_categories(table, cats)
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, table)
        else:
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        matchAnalyseBoxScore(game, table)


def matchFilterByValues(game, table, BSWindow):
    filterWindow = filterByValues_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        auxCats = cats.split(", ")
        auxCats = list(map(lambda x: x.split(": "), auxCats))
        cats = {}
        for cat in auxCats:
            cats[cat[0]] = int(cat[1])

        newTable = game.filter_by_value(table, cats)
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, table)
        else:
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        matchAnalyseBoxScore(game, table)


def matchFilterByTop(game, table, BSWindow):
    filterWindow = filterByTop_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        cats = cats.split(", ")

        newTable = game.top_players(table, cats, n=int(values['n']), max=values['Condition']=="maximum")
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, table)
        else:
            filterWindow.close()
            BSWindow.close()
            matchAnalyseBoxScore(game, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        matchAnalyseBoxScore(game, table)


def matchAnalyseBoxScore(game, table):
    window = analyseBoxScore_menu(game, table)

    while True:
        event, values = window.read()
        if event == 'Help':
            helpWindow = helpAnalyseBoxScore_menu(table.columns.tolist())
            _, _ = helpWindow.read()
        elif event == 'Filter by players':
            matchFilterByPlayers(game, table, window)
            break
        elif event == 'Filter by categories':
            matchFilterByCategories(game, table, window)
            break
        elif event == 'Filter by values':
            matchFilterByValues(game, table, window)
            break
        elif event == 'Get top players':
            matchFilterByTop(game, table, window)
            break
        elif event == 'Save':
            game.save_box_score(table, name=values['SaveFile'])
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
            window.FindElement('SaveFile').Update('')
        elif event == 'Back':
            window.close()
            matchChooseBoxScore(game)
            break
        elif event == sg.WIN_CLOSED:
            break


def matchChooseBoxScore(game):
    window = matchChooseBoxScore_menu()
    event, values = window.read()

    if event == 'OK':
        start = values['Start']
        if start == "":
            start = None
        end = values['End']
        if end == "":
            end = None
        if values['Local'] and values['Visiting']:
            table = game.get_box_scores(team=0, start=start, end=end)
        else:
            boxScores = game.get_box_scores(start=start, end=end)
            if values['Local']:
                table = boxScores[0]
            elif values['Visiting']:
                table = boxScores[1]
        window.close()
        matchAnalyseBoxScore(game, table)
    elif event == 'Back':
        window.close()
        analyseMatch(game)

### 1.2. Match statistics
def matchStatistics(game, timestamp=""):
    window = matchStatistics_menu(game, timestamp)
    event, values = window.read()

    if event == 'OK':
        window.close()
        matchStatistics(game, values['Time']) 
    elif event == 'Back':
        window.close()
        analyseMatch(game)


### 1.3. Playing times
def playingTimes(game):
    window = playingTimes_menu(game)
    while True:
        event, values = window.read()

        if event == 'Time OK':
            window['Team 1'].update(game.home)
            window['Team 2'].update(game.away)
            
            fives = game.five_on_court(values['Time input'])
            for team in range(1,3):
                if isinstance(fives[team-1],list):
                    window[f'Time output {team}'].update(str(fives[team-1][0]) + "\n" + str(fives[team-1][1]))
                else:
                    window[f'Time output {team}'].update(str(fives[team-1]))

        elif event == 'Player OK':
            team = values['Team player input']
            if get_team(team) == game.home:
                team = 1
            elif get_team(team) == game.away:
                team = 2
            window['Player output'].update(game.intervals_of_player(team, values['Player input']))

        elif event == 'Five OK':
            team = values['Team five input']
            if get_team(team) == game.home:
                team = 1
            elif get_team(team) == game.away:
                team = 2
            players = values['Five input'].split(", ")
            intervals = game.intervals_of_five(team, players)
            window['Five output'].update(intervals)

        elif event == 'Back':
            window.close()
            analyseMatch(game)
            break

        elif event == sg.WIN_CLOSED:
            break

### 1.4. Shooting statistics
def shootingStatisticsTable(Event, team, table):
    window = shootingStatisticsTable_menu(Event, table)
    
    while True:
        event, _ = window.read()
        if event == 'Save':
            Event.save_shooting_table(team, table)
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            shootingStatistics(Event)
            break
        elif event == sg.WIN_CLOSED:
            break


def shootingStatisticsPlot(Event, team, table):
    window = statisticsPlot_menu()

    while True:
        event, _ = window.read()
        plot = Event.get_shooting_plot(team, table)

        if event == 'Show plot':
            plot.show()
        elif event == 'Save plot':
            Event.save_shooting_plot(team, plot)
            sg.PopupTimed("Plot saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            shootingStatistics(Event)
            break
        elif event == sg.WIN_CLOSED:
            break


def shootingStatistics(Event):
    try:
        Event.home
        window = shootingStatisticsMatch_menu()
    except:
        window = shootingStatisticsSeason_menu()
    event, values = window.read()

    if values.get('Local', False) or values.get('Own team', False):
        team = 1
    elif values.get('Visiting', False) or values.get('Opponents', False):
        team = 2
    
    if event != sg.WIN_CLOSED:
        table = Event.get_shooting_table(team)

    if event == 'Shooting statistics table':
        window.close()
        shootingStatisticsTable(Event, team, table)
    elif event == 'Shooting statistics plot':
        window.close()
        shootingStatisticsPlot(Event, team, table)
    elif event == 'Back':
        window.close()
        try:
            Event.home
            analyseMatch(Event)
        except:
            analyseSeason(Event)


### 1.5. Assist statistics
def assistStatisticsMatrix(game, team):
    window = assistStatisticsMatrix_menu(game, team)
    
    while True:
        event, _ = window.read()
        if event == 'Save':
            game.save_assist_matrix(team)
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            matchAssistStatistics(game)
            break
        elif event == sg.WIN_CLOSED:
            break


def assistStatisticsPlot(game, team):
    window = statisticsPlot_menu()

    while True:
        event, _ = window.read()

        if event == 'Show plot':
            plot = game.get_assist_plot(team)
            plot.show()
        elif event == 'Save plot':
            game.save_assist_plot(team)
            sg.PopupTimed("Plot saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            matchAssistStatistics(game)
            break
        elif event == sg.WIN_CLOSED:
            break


def matchAssistStatistics(game):
    window = assistStatistics_menu()
    event, values = window.read()

    if values['Local']:
        team = 1
    elif values['Visiting']:
        team = 2

    if event == 'Assist statistics matrix':
        window.close()
        assistStatisticsMatrix(game, team)
    elif event == 'Assist statistics plot':
        window.close()
        assistStatisticsPlot(game, team)
    elif event == 'Back':
        window.close()
        analyseMatch(game)


### 1.6. PbP
def visualPbP(game):
    back = game.visual_PbP(True)
    if back:
        seePbP(game)


def textPbP(game):
    window = textPbP_menu(game)
    while True:
        event, _ = window.read()
        if event == 'Help':
            helpWindow = helpTextPbP_menu()
            _, _ = helpWindow.read()
        elif event == 'Back':
            window.close()
            seePbP(game)
            break
        elif event == sg.WIN_CLOSED:
            break


def seePbP(game):
    window = seePbP_menu()
    event, _ = window.read()

    if event == 'Text mode':
        window.close()
        textPbP(game)
    elif event == 'Visual mode':
        window.close()
        visualPbP(game)
    elif event == 'Back':
        window.close()
        analyseMatch(game)

## 1. Analyse match
def analyseMatch(game):
    window = analyseMatch_menu()
    event, _ = window.read()

    if event == 'Box scores':
        window.close()
        matchChooseBoxScore(game)
    elif event == 'Match statistics':
        window.close()
        matchStatistics(game)
    elif event == 'Playing times':
        window.close()
        playingTimes(game)
    elif event == 'Shooting statistics':
        window.close()
        shootingStatistics(game)
    elif event == 'Assist statistics':
        window.close()
        matchAssistStatistics(game)
    elif event == 'See play-by-play':
        window.close()
        seePbP(game)
    elif event == 'Back':
        window.close()
        defineMatch()


def defineMatch():
    window = defineMatch_menu()
    event, values = window.read()

    if event == 'OK':
        game = Match(values['Home'], values['Away'], values['Date'])
        window.close()
        analyseMatch(game)
    elif event == 'Back':
        window.close()
        main()

## 2. Analyse season
def statisticTable(season, table, statistic, category, player):
    window = statisticTable_menu(season, table, statistic)

    while True:
        event, _ = window.read()

        if event == 'Save':
            if statistic == "box score":
                auxPlayer = player.replace(" ", "")
                name = category + "-" + auxPlayer
            else:
                # "greatest streak" -> "GreatestStreak"
                auxStatistic = statistic.split()
                auxStatistic = list(map(lambda x: x.capitalize(), auxStatistic))
                auxStatistic = ("").join(auxStatistic)
                name = auxStatistic
            name += "Table"
            season.save_statistic_evolution_table(table, name)
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
            
        elif event == 'Back':
            window.close()
            statisticAnalysis(season, table, statistic, category, player)
            break

        elif event == sg.WIN_CLOSED:
            break


def statisticAnalysis(season, table, statistic, category, player):
    window = statisticAnalysis_menu()

    while True:
        event, _ = window.read()

        if event == 'See table':
            window.close()
            statisticTable(season, table, statistic, category, player)
            break

        if event == 'Show plot':
            plot = season.get_statistic_evolution_plot(statistic, category, player, table)
            plot.show()

        elif event == 'Save plot':
            plot = season.get_statistic_evolution_plot(statistic, category, player, table)
            if statistic == "box score":
                auxPlayer = player.replace(" ", "")
                name = category + "-" + auxPlayer
            else:
                # "greatest streak" -> "GreatestStreak":
                auxStatistic = statistic.split()
                auxStatistic = list(map(lambda x: x.capitalize(), auxStatistic))
                auxStatistic = ("").join(auxStatistic)
                name = auxStatistic
            name += "Plot"
            season.save_statistic_evolution_plot(plot, name)
            sg.PopupTimed("Plot saved", auto_close_duration=1, button_type=5)
        
        elif event == 'Back':
            window.close()
            statisticElection(season)
            break

        elif event == sg.WIN_CLOSED:
            break


def statisticElection(season):
    window = statisticElection_menu()
    event, values = window.read()

    if event == 'OK':
        if values['BS']:
            statistic = "box score"
            category = values['Category']
            player = values['Player']
            if player == "":
                player = None
            table = season.get_statistic_evolution_table(statistic, category, player)
        else:
            if values['Difference']:
                statistic = "greatest difference"
            if values['Streak']:
                statistic = "greatest streak"
            elif values['Partial']:
                statistic = "greatest partial"
            elif values['Drought']:
                statistic = "longest drought"
            table = season.get_statistic_evolution_table(statistic)     
            category = player = None
        
        window.close()
        statisticAnalysis(season, table, statistic, category, player)
    
    elif event == 'Back':
        window.close()
        analyseSeason(season)


def calendar(season):
    window = calendar_menu(season)

    while True:
        event, _ = window.read()
        if event == 'Save':
            season.save_calendar()
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            analyseSeason(season)
            break
        elif event == sg.WIN_CLOSED:
            break


def resultsTable(season):
    window = resultsTable_menu(season)

    while True:
        event, _ = window.read()
        if event == 'Save':
            season.save_results_table()
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            results(season)
            break
        elif event == sg.WIN_CLOSED:
            break


def resultsPlot(season):
    window = resultsPlot_menu()

    while True:
        event, values = window.read()

        if values['Condition'] == "Team":
            plotId = 1
        elif values['Condition'] == "Opponent team":
            plotId = 2
        elif values['Condition'] == "Both":
            plotId = 3
        else:
            plotId = 4

        if event == 'Show plot':
            plot = season.get_results_plot(plotId)
            plot.show()
        elif event == 'Save plot':
            season.save_results_plot(plotId)
            sg.PopupTimed("Plot saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            results(season)
            break
        elif event == sg.WIN_CLOSED:
            break


def results(season):
    window = results_menu()
    event, _ = window.read()
    if event == 'See results table':
        window.close()
        resultsTable(season)
    elif event == 'Results plot':
        window.close()
        resultsPlot(season)
    elif event == 'Back':
        window.close()
        analyseSeason(season)


def seasonFilterByPlayers(season, table, BSWindow):
    filterWindow = filterByPlayers_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        players = values['Filter condition']
        players = players.split(", ")

        newTable = season.filter_by_players(table, players)
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, table)
        else:
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        seasonAnalyseBoxScore(season, table)


def seasonFilterByCategories(season, table, BSWindow):
    filterWindow = filterByCategories_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        if not (isinstance(cats,str) and cats in ("simple", "shooting", "rebounding")):
            cats = cats.split(", ")

        newTable = season.filter_by_categories(table, cats)
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, table)
        else:
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        seasonAnalyseBoxScore(season, table)


def seasonFilterByValues(season, table, BSWindow):
    filterWindow = filterByValues_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        auxCats = cats.split(", ")
        auxCats = list(map(lambda x: x.split(": "), auxCats))
        cats = {}
        for cat in auxCats:
            cats[cat[0]] = float(cat[1])

        newTable = season.filter_by_value(table, cats)
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, table)
        else:
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        seasonAnalyseBoxScore(season, table)


def seasonFilterByTop(season, table, BSWindow):
    filterWindow = filterByTop_menu(table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        cats = cats.split(", ")

        newTable = season.top_players(table, cats, n=int(values['n']), max=values['Condition']=="maximum")
        if newTable is None or len(newTable) == 0:
            sg.PopupTimed("There are no records that meet the introduced conditions", auto_close_duration=3, button_type=5)
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, table)
        else:
            filterWindow.close()
            BSWindow.close()
            seasonAnalyseBoxScore(season, newTable)
    elif event == sg.WIN_CLOSED:
        BSWindow.close()
        seasonAnalyseBoxScore(season, table)


def seasonAnalyseBoxScore(season, table):
    window = analyseBoxScore_menu(season, table)

    while True:
        event, values = window.read()
        if event == 'Help':
            helpWindow = helpAnalyseBoxScore_menu(table.columns.tolist())
            _, _ = helpWindow.read()
        elif event == 'Filter by players':
            seasonFilterByPlayers(season, table, window)
            break
        elif event == 'Filter by categories':
            seasonFilterByCategories(season, table, window)
            break
        elif event == 'Filter by values':
            seasonFilterByValues(season, table, window)
            break
        elif event == 'Get top players':
            seasonFilterByTop(season, table, window)
            break
        elif event == 'Save':
            season.save_box_score(table, name=values['SaveFile'])
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
            window.FindElement('SaveFile').Update('')
        elif event == 'Back':
            window.close()
            seasonChooseBoxScore(season)
            break
        elif event == sg.WIN_CLOSED:
            break


def seasonChooseBoxScore(season):
    window = seasonChooseBoxScore_menu()
    event, _ = window.read()

    if event == 'Total values':
        table = season.get_box_score(1)
        window.close()
        seasonAnalyseBoxScore(season, table)
    elif event == 'Per game values':
        table = season.get_box_score(2)
        window.close()
        seasonAnalyseBoxScore(season, table)
    elif event == 'Per 36 minutes values':
        table = season.get_box_score(3)
        window.close()
        seasonAnalyseBoxScore(season, table)
    elif event == 'Back':
        window.close()
        analyseSeason(season)


def assistStatisticsMatrixSeason(season, matrix):
    window = assistStatisticsMatrixSeason_menu(matrix)

    while True:
        event, _ = window.read()

        if event == 'Save':
            season.save_assist_matrix(matrix)
            sg.PopupTimed("Table saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            seasonAssistStatistics(season, matrix)
            break
        elif event == sg.WIN_CLOSED:
            break


def seasonAssistStatistics(season, matrix):
    window = assistStatisticsSeason_menu()

    while True:
        event, _ = window.read()

        if event == 'See table':
            window.close()
            assistStatisticsMatrixSeason(season, matrix)
            break
        elif event == 'Show plot':
            plot = season.get_assist_plot(matrix)
            plot.show()
        elif event == 'Save plot':
            plot = season.get_assist_plot(matrix)
            season.save_assist_plot(plot)
            sg.PopupTimed("Plot saved", auto_close_duration=1, button_type=5)
        elif event == 'Back':
            window.close()
            analyseSeason(season)
            break
        elif event == sg.WIN_CLOSED:
            break


def analyseSeason(season):
    window = analyseSeason_menu()
    event, _ = window.read()

    if event == 'See calendar':
        window.close()
        calendar(season)
    elif event == 'See results':
        window.close()
        results(season)
    elif event == 'Box score':
        window.close()
        seasonChooseBoxScore(season)
    if event == 'Statistic evolution':
        window.close()
        statisticElection(season)
    elif event == 'Shooting statistics':
        window.close()
        shootingStatistics(season)
    elif event == 'Assist statistics':
        assists = season.get_assist_matrix()
        window.close()
        seasonAssistStatistics(season, assists)
    elif event == 'Back':
        window.close()
        defineSeason()


def defineSeason():
    window = defineSeason_menu()
    event, values = window.read()

    if event == 'OK':
        season = Season(values['Team'], values['Season'])
        window.close()
        analyseSeason(season)
    elif event == 'Back':
        window.close()
        main()


def main():
    window = main_menu()
    event, _ = window.read()

    if event == 'Analyse match':
        window.close()
        defineMatch()

    elif event == 'Analyse season':
        window.close()
        defineSeason()

if __name__ == '__main__':
    main()