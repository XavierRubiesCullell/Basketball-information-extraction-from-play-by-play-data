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
def chooseBoxScore_menu():
    inputSize = (15,1)
    layout = [
        [ sg.Text("Choose the time interval you desire:") ],
        [ sg.Input(key='Start', size=inputSize, tooltip="Introduce the time in format quarter:MM:SS\nquarter can be '1Q','2Q','3Q','4Q','xOT\nIf nothing is written, the beginning of the match will be considered"),
         sg.Input(key='End', size=inputSize, tooltip="Introduce the time in format quarter:MM:SS\nquarter can be '1Q','2Q','3Q','4Q','xOT\nIf nothing is written, the end of the match will be considered")],
        [ sg.Text("Choose the box score you desire:") ],
        #[ sg.Button('Local'), sg.Button('Visiting'), sg.Button('Both')],
        [ sg.Checkbox("Local", key = 'Local'), sg.Checkbox("Visiting", key = 'Visiting')],
        [ sg.Button('OK')],
        [ sg.Text("")],
        [ sg.Button('Back')]
    ]
    return sg.Window("Box score election menu", layout)

def helpAnalyseBoxScore_menu(cols):
    textSize = (9, 1)
    explanation = {
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
    # word = ""
    # for cat in cols:
    #     word += cat + ":" + " "*10 + explanation[cat] + "\n"
    # layout2 = [
    #     [sg.Text(word)]
    # ]
    if cols[0] == 'Team':
        del cols[0]
    if cols[0] == 'Mins':
        del cols[0]
    layout = [
        [sg.Text(cat, size=textSize), sg.Text(explanation[cat])] for cat in cols
    ]
    return sg.Window("Help Menu", layout)

def analyseBoxScore_menu(game, table):
    auxTable = create_table(table, "Player")
    indentation = (1,1)
    layout = [
        [ sg.Button('Help') ],
        [ sg.Table(values=auxTable.values.tolist(), headings=auxTable.columns.tolist(), num_rows=len(auxTable), alternating_row_color = 'gray', hide_vertical_scroll = True) ],
        [ sg.Text("Filter:") ],
        [ sg.Button('Filter by players'), sg.Button('Filter by categories'), sg.Button('Filter by values'), sg.Button('Get top players') ],
        [ sg.Text("Save:") ],
        [
            sg.Text("", size=indentation),
            sg.Text("The box score will be saved in: " + game.home + "_" + game.away + "_" + convert_date_match(game.date) + "_BS_"),
            sg.Input(key='SaveFile', size = (15,1)),
            sg.Text(".csv"),
            sg.Button('Save')
        ],
        [ sg.Text("")],
        [ sg.Button('Back')]
    ]
    return sg.Window("Box score menu", layout)

def filterByPlayers_menu(game, table):
    layout = [
        [ sg.Text("List of players") ],
        [ sg.Input(key='Filter condition', tooltip="Format: player1, player2, player3, ..."), sg.Button('Filter') ]
    ]
    return sg.Window("Filter by players Menu", layout)

def filterByCategories_menu(game, table):
    layout = [
        [ sg.Text("List of categories") ],
        [ sg.Input(key='Filter condition', tooltip="Format: category1, category2, category3, ..."), sg.Button('Filter') ]
    ]
    return sg.Window("Filter by categories Menu", layout)

def filterByValues_menu(game, table):
    layout = [
        [ sg.Text("List of categories and their corresponding values") ],
        [ sg.Input(key='Filter condition', tooltip="Format: category1: value1, category2: value2, category3: value3, ..."), sg.Button('Filter') ]
    ]
    return sg.Window("Filter by values Menu", layout)

def filterByTop_menu(game, table):
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
def matchStatistics_menu(game):
    table1 = create_table(game.quarter_scorings(), " ")
    layout1 = [
        [ sg.Table(values=table1.values.tolist(),
        headings = table1.columns.tolist(),
        col_widths = [5]*len(table1.columns),
        auto_size_columns = False,
        num_rows=len(table1),
        hide_vertical_scroll = True,
        row_height = 20) ]
    ]

    table2 = pd.DataFrame(np.array((
        ["Greatest difference"]+list(game.greatest_difference()),
        ["Greatest partial"]+list(game.greatest_partial()),
        ["Greatest streak"]+list(game.greatest_streak()),
        ["Longest drought"]+list(game.longest_drought())
        )), columns = ("Statistic", game.home, game.away))
    layout2 = [
        [ sg.Table(values=table2.values.tolist(), headings=table2.columns.tolist(), num_rows=len(table2), hide_vertical_scroll = True, row_height = 20) ]
    ]
    
    layout = [
        [ sg.Text("Match Statistics Menu") ],
        [ sg.Text("Quarter scorings:") ],
        layout1,
        [ sg.Text("") ],
        [ sg.Text("Match statistics:") ],
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

def shootingStatisticsTable_menu(game, team):
    table = game.get_shooting_table()[team-1]
    table = create_table(table, "Distance (ft)")
    layout = [
        [ sg.Button('Save') ],
        [ sg.Table(values=table.values.tolist(), headings=table.columns.tolist(), num_rows=len(table), hide_vertical_scroll = True) ],
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

def shootingStatistics_menu():
    layout = [
        [ sg.Text("Shooting statistics Menu") ],
        [ sg.Button('Shooting statistics table') ],
        [ sg.Button('Shooting statistics plot') ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Shooting statistics Menu", layout)

### 1.5. Assist statistics
def assistStatisticsMatrix_menu(game, team):
    table = game.get_assist_matrix(team)
    table = create_table(table, " ")
    layout = [
        [ sg.Button('Save') ],
        [ sg.Table(values=table.values.tolist(), headings=table.columns.tolist(), num_rows=len(table), hide_vertical_scroll = True) ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Assist statistics matrix Menu", layout)

def assistStatistics_menu():
    layout = [
        [ sg.Text("Assist statistics Menu") ],
        [ sg.Button('Assist statistics matrix') ],
        [ sg.Button('Assist statistics plot') ],
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
    textSize = (12, 1)
    layout = [
        [ sg.Text("S, 2, 5, O:", size=textSize), sg.Text("2-point shot from 5ft that went out") ],
        [ sg.Text("S, 2, 5, I A 23:", size=textSize), sg.Text("2-point shot from 5ft that went in, assisted by #23") ],
        [ sg.Text("R, O/D:", size=textSize), sg.Text("offensive/deffensive rebound") ],
        [ sg.Text("T:", size=textSize), sg.Text("turnover") ],
        [ sg.Text("St, 23:", size=textSize), sg.Text("steal, the ball was stolen from #23") ],
        [ sg.Text("B, 23:", size=textSize), sg.Text("block, #23 was its receiver") ],
        [ sg.Text("F, 23:", size=textSize), sg.Text("foul, drawn by #23") ],
        [ sg.Text("C, 23:", size=textSize), sg.Text("change, #23 is the one that enters the game") ]
    ]
    return sg.Window("Help Menu", layout)

def textPbP_menu(game):
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
        [ sg.Text("Text play-by-play Menu", size=(66,1)), sg.Button('Help') ],
        [ sg.Table(values=plays.values.tolist(), headings=cols, justification="left", num_rows=20, row_height=15) ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Text play-by-play Menu", layout)

def visualPbP_menu(game):
    layout = [
        [ sg.Button("Pause", key='Pause/Resume') ],
        [ sg.Text(key="ActionText", size=(40,1)) ],
        [ sg.Image(key="ActionImage") ],
        [ sg.Text("", size=(10,1), key="Clock"),
            sg.Text(game.home),
            sg.Text("", size=(3,1), key="Score1"),
            sg.Text(game.away),
            sg.Text("", size=(2,1), key="Score2") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Visual PbP", layout)

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
        [ sg.Button('See calendar', size = buttonSize)],
        [ sg.Button('Statistic evolution', size = buttonSize)],
        [ sg.Text("")],
        [ sg.Button('Back')]
    ]
    return sg.Window("Analyse Season Menu", layout)

def calendar_menu(season):
    auxTable = create_table(season.matchTable, "Player")
    layout = [
        [ sg.Button('Save') ],
        [   sg.Table(values=auxTable.values.tolist(),
            headings=auxTable.columns.tolist(),
            alternating_row_color = 'gray') ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Calendar Menu", layout)

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
            sg.Input(key='Player', size=(20,1), tooltip="If no input is given, team value is considered") ],
        [ sg.Button('OK', size=buttonSize) ],
        [ sg.Text("*Box score is slow (takes about 2 minutes) and program may warn it is not answering, but just let it work") ],
        [ sg.Text("") ],
        [ sg.Button('Back', size=buttonSize) ]
    ]
    return sg.Window("Statistic Evolution Menu", layout)

def statisticAnalysis_menu():
    buttonSize = (20,1)
    layout = [
        [ sg.Text("Statistic analysis menu") ],
        [ sg.Button('See table', size = buttonSize) ],
        [ sg.Button('See plot', size = buttonSize) ],
        [ sg.Button('Save plot', size = buttonSize) ],
        [ sg.Text("") ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Statistic Analysis Menu", layout)

def statisticTable_menu(season, table, statistic):
    auxTable = create_table(table, "Match")
    layout = [
        [ sg.Button('Save') ],
        [   sg.Table(values=auxTable.values.tolist(),
            headings=auxTable.columns.tolist(),
            alternating_row_color = 'gray') ],
        [ sg.Button('Back') ]
    ]
    return sg.Window("Statistic Table Menu", layout)

# ----------------------------------------------------------------------------------
# INTERACTIVE FUNCTIONS

### 1.1. Box score
def filterByPlayers(game, table, BSWindow):
    filterWindow = filterByPlayers_menu(game, table)
    event, values = filterWindow.read()
    if event == 'Filter':
        players = values['Filter condition']
        players = players.split(", ")
        table = game.filter_by_players(table, players)
        filterWindow.close()
        BSWindow.close()
        analyseBoxScore(game, table)


def filterByCategories(game, table, BSWindow):
    filterWindow = filterByCategories_menu(game, table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        if not (isinstance(cats,str) and cats in ("simple", "shooting", "rebounding")):
            cats = cats.split(", ")
        table = game.filter_by_categories(table, cats)
        filterWindow.close()
        BSWindow.close()
        analyseBoxScore(game, table)


def filterByValues(game, table, BSWindow):
    filterWindow = filterByValues_menu(game, table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        auxCats = cats.split(", ")
        auxCats = list(map(lambda x: x.split(": "), auxCats))
        cats = {}
        for cat in auxCats:
            cats[cat[0]] = int(cat[1])

        table = game.filter_by_value(table, cats)
        filterWindow.close()
        BSWindow.close()
        analyseBoxScore(game, table)


def filterByTop(game, table, BSWindow):
    filterWindow = filterByTop_menu(game, table)
    event, values = filterWindow.read()
    if event == 'Filter':
        cats = values['Filter condition']
        cats = cats.split(", ")
        table = game.top_players(table, cats, n=int(values['n']), max=values['Condition']=="maximum")
        filterWindow.close()
        BSWindow.close()
        analyseBoxScore(game, table)


def analyseBoxScore(game, table):
    window = analyseBoxScore_menu(game, table)

    while True:
        event, values = window.read()
        if event == 'Help':
            helpWindow = helpAnalyseBoxScore_menu(table.columns.tolist())
            helpEvent, _ = helpWindow.read()
            if helpEvent == sg.WIN_CLOSED:
                helpWindow.close()
        elif event == 'Filter by players':
            filterByPlayers(game, table, window)
        elif event == 'Filter by categories':
            filterByCategories(game, table, window)
        elif event == 'Filter by values':
            filterByValues(game, table, window)
        elif event == 'Get top players':
            filterByTop(game, table, window)
        elif event == 'Save':
            game.save_box_score(table, name=values['SaveFile'])
            window.close()
            analyseBoxScore(game, table)
            break
        elif event == 'Back':
            window.close()
            chooseBoxScore(game)
            break
        elif event == sg.WIN_CLOSED:
            window.close()
            break


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
    elif event == 'Back':
        window.close()
        analyseMatch(game)

### 1.2. Match statistics
def matchStatistics(game):
    window = matchStatistics_menu(game)
    event, _ = window.read()

    if event == 'Back':
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
            window.close()
            break

### 1.4. Shooting statistics
def shootingStatisticsTable(game, team):
    window = shootingStatisticsTable_menu(game, team)
    event, _ = window.read()
    if event == 'Save':
        window.close()
        game.save_shooting_table(team)
        shootingStatisticsTable(game, team)

    elif event == 'Back':
        window.close()
        shootingStatisticsTableElection(game)


def shootingStatisticsTableElection(game):
    window = teamElection_menu()
    event, values = window.read()

    if event == 'OK':
        window.close()
        if values['Local']:
            window.close()
            shootingStatisticsTable(game, 1)
        elif values['Visiting']:
            window.close()
            shootingStatisticsTable(game, 2)

    elif event == 'Back':
        window.close()
        shootingStatistics(game)


def shootingStatisticsPlot(game, team):
    window = statisticsPlot_menu()
    event, _ = window.read()

    if event == 'Show plot':
        plot = game.get_shooting_plot(team)
        plot.show()
        window.close()
        shootingStatisticsPlot(game, team)
    elif event == 'Save plot':
        game.save_shooting_plot(team)
        window.close()
        shootingStatisticsPlot(game, team)
    elif event == 'Back':
        window.close()
        shootingStatisticsPlotElection(game)

def shootingStatisticsPlotElection(game):
    window = teamElection_menu()
    event, values = window.read()

    if event == 'OK':
        window.close()
        if values['Local']:
            window.close()
            shootingStatisticsPlot(game, 1)
        elif values['Visiting']:
            window.close()
            shootingStatisticsPlot(game, 2)

    elif event == 'Back':
        window.close()
        shootingStatistics(game)


def shootingStatistics(game):
    window = shootingStatistics_menu()
    event, _ = window.read()

    if event == 'Shooting statistics table':
        window.close()
        shootingStatisticsTableElection(game)
    elif event == 'Shooting statistics plot':
        window.close()
        shootingStatisticsPlotElection(game)
    elif event == 'Back':
        window.close()
        analyseMatch(game)


### 1.5. Assist statistics
def assistStatisticsMatrix(game, team):
    window = assistStatisticsMatrix_menu(game, team)
    print("hola, aqui falla")
    event, _ = window.read()
    if event == 'Save':
        window.close()
        game.save_assist_matrix(team)
        assistStatisticsMatrix(game, team)
    elif event == 'Back':
        window.close()
        assistStatisticsMatrixElection(game)


def assistStatisticsMatrixElection(game):
    window = teamElection_menu()
    event, values = window.read()

    if event == 'OK':
        window.close()
        if values['Local']:
            window.close()
            assistStatisticsMatrix(game, 1)
        elif values['Visiting']:
            window.close()
            assistStatisticsMatrix(game, 2)

    elif event == 'Back':
        window.close()
        assistStatistics(game)


def assistStatisticsPlot(game, team):
    window = statisticsPlot_menu()
    event, _ = window.read()

    if event == 'Show plot':
        plot = game.get_assist_plot(team)
        plot.show()
        window.close()
        assistStatisticsPlot(game, team)
    elif event == 'Save plot':
        game.save_assist_plot(team)
        window.close()
        assistStatisticsPlot(game, team)
    elif event == 'Back':
        window.close()
        assistStatisticsPlotElection(game)


def assistStatisticsPlotElection(game):
    window = teamElection_menu()
    event, values = window.read()

    if event == 'OK':
        window.close()
        if values['Local']:
            window.close()
            assistStatisticsPlot(game, 1)
        elif values['Visiting']:
            window.close()
            assistStatisticsPlot(game, 2)

    elif event == 'Back':
        window.close()
        assistStatistics(game)


def assistStatistics(game):
    window = assistStatistics_menu()
    event, _ = window.read()

    if event == 'Assist statistics matrix':
        window.close()
        assistStatisticsMatrixElection(game)
    
    elif event == 'Assist statistics plot':
        window.close()
        assistStatisticsPlotElection(game)

    elif event == 'Back':
        window.close()
        analyseMatch(game)


### 1.6. PbP
def visualPbP(game):
    window = visualPbP_menu(game)
    back = game.visual_PbP(window)
    if back:
        seePbP(game)


def textPbP(game):
    window = textPbP_menu(game)
    while True:
        event, _ = window.read()
        if event == 'Help':
            helpWindow = helpTextPbP_menu()
            helpEvent, _ = helpWindow.read()
            if helpEvent == sg.WIN_CLOSED:
                helpWindow.close()

        elif event == 'Back':
            window.close()
            seePbP(game)
            break

        elif event == sg.WIN_CLOSED:
            window.close()
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
        chooseBoxScore(game)
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
        assistStatistics(game)
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
    event, _ = window.read()

    if event == 'Save':
        window.close()
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
        statisticTable(season, table, statistic, category, player)
    elif event == 'Back':
        window.close()
        statisticAnalysis(season, table, statistic, category, player)


def statisticAnalysis(season, table, statistic, category, player):
    window = statisticAnalysis_menu()
    event, _ = window.read()

    if event == 'See table':
        window.close()
        statisticTable(season, table, statistic, category, player)
    if event == 'See plot':
        window.close()
        season.get_statistic_evolution_plot(statistic, category, player, table).show()
        statisticAnalysis(season, table, statistic, category, player)
    elif event == 'Save plot':
        plot = season.get_statistic_evolution_plot(statistic, category, player, table)
        if statistic == "box score":
            auxPlayer = player.replace(" ", "")
            name = category + "-" + auxPlayer
        else:
            # "greatest streak" -> "GreatestStreak"
            auxStatistic = statistic.split()
            auxStatistic = list(map(lambda x: x.capitalize(), auxStatistic))
            auxStatistic = ("").join(auxStatistic)
            name = auxStatistic
        name += "Plot"
        season.save_statistic_evolution_plot(plot, name)
        window.close()
        statisticAnalysis(season, table, statistic, category, player)
    
    elif event == 'Back':
        window.close()
        statisticElection(season)


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
    event, _ = window.read()

    if event == 'Save':
        window.close()
        season.save_calendar()
        calendar(season)
    elif event == 'Back':
        window.close()
        analyseSeason(season)


def analyseSeason(season):
    window = analyseSeason_menu()
    event, _ = window.read()

    if event == 'Statistic evolution':
        window.close()
        statisticElection(season)
    if event == 'See calendar':
        window.close()
        calendar(season)
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