import PySimpleGUI as sg
from MatchClass import Match

def mainMenu():
    layout = [
        [ sg.Text("Main Menu") ],
        [ sg.Button('Analyse match')],
        [ sg.Button('Analyse season')]
    ]
    return sg.Window("Main Menu", layout)

def defineMatchMenu():
    layout = [
        [ sg.Text("Match definition menu") ],
        [ sg.Text("Home"), sg.Input(key='Home')],
        [ sg.Text("Away"), sg.Input(key='Away')],
        [ sg.Text("Date"), sg.Input(key='Date')],
        [ sg.Button('OK')],
        [ sg.Text("")],
        [ sg.Button('Back to main menu')]
    ]
    return sg.Window("Define Match Menu", layout)

def analyseMatchMenu():
    layout = [
        [ sg.Text("Match analysis menu") ],
        [ sg.Button('Box scores')],
        [ sg.Button('Match statistics')],
        [ sg.Button('Playing times')],
        [ sg.Button('Assists statistics')],
        [ sg.Button('Shooting statistics')],
        [ sg.Button('See play-by-play')],
        [ sg.Text("")],
        [ sg.Button('Back to define match menu')]
    ]
    return sg.Window("Analyse Match Menu", layout)

def chooseBoxScoreMenu():
    layout = [
        [ sg.Text("Choose the time interval you desire") ],
        [ sg.Input(key='Start')], [sg.Input(key='End')],
        [ sg.Text("Choose the box score you desire") ],
        [ sg.Button('Local'), sg.Button('Visiting'), sg.Button('Both')],
        [ sg.Text("")],
        [ sg.Button('Back to analyse match menu')]
    ]
    return sg.Window("Box score election menu", layout)

def create_table(table):
    tableAux = table.copy()
    tableAux['Player'] = tableAux.index
    cols = tableAux.columns.tolist()
    cols = [cols[-1]] + cols[:-1]
    tableAux = tableAux[cols]
    tabValues = tableAux.values.tolist()
    return sg.Table(values=tabValues, headings=cols, num_rows=len(tabValues), auto_size_columns=True, key='Taula')

def analyseBoxScoreMenu(table):
    layout = [
        [create_table(table)],
        [sg.Input(key='Filter')],
        [sg.Button('Filter by players'), sg.Button('Filter by categories'), sg.Button('Filter by value')],
        [sg.Input(key='SaveFile'), sg.Button('Save')],
        [ sg.Text("")],
        [ sg.Button('Back to choose box score menu')]
    ]
    return sg.Window("Box score menu", layout)


def analyseBoxScore(game, table):
    window = analyseBoxScoreMenu(table)
    event, values = window.read()

    window.close()
    try:
        if event == 'Filter by players':        
            table = game.filter_by_players(values['Filter'].split(", "), table)
            analyseBoxScore(game, table)

        elif event == 'Filter by categories':
            cats = values['Filter']
            if "," in cats:
                cats = cats.split(", ")
            table = game.filter_by_categories(cats, table)
            analyseBoxScore(game, table)

        elif event == 'Filter by value':
            cats = values['Filter']
            auxCats = cats.split(", ")
            auxCats = list(map(lambda x: x.split(": "), auxCats))
            cats = {}
            for cat in auxCats:
                cats[cat[0]] = int(cat[1])
            table = game.filter_by_value(cats, table)
            analyseBoxScore(game, table)
        
        elif event == 'Save':
            game.box_score_save(table, pkl=values['SaveFile'], folder="Files/")
            analyseBoxScore(game, table)
    except:
        sg.popup_error("There was an error in your input. Please check the syntax you need to use")
    if event == 'Back to choose box score menu':
        window.close()
        chooseBoxScore(game)


def chooseBoxScore(game):
    window = chooseBoxScoreMenu()
    event, values = window.read()

    if event == 'Back to analyse match menu':
        window.close()
        analyseMatch(game)
    else:
        if event == 'Both':
            table = game.box_scores(start=values['Start'], end=values['End'], joint=True)
        else:
            boxScores = game.box_scores(start=values['Start'], end=values['End'])
            if event == 'Local':
                table = boxScores[0]
            elif event == 'Visiting':
                table = boxScores[1]
        window.close()
        analyseBoxScore(game, table)


def matchStatistics(game):
    drought = game.longest_drought()
    partial = game.greatest_partial()
    streak = game.greatest_streak()
    layout = [
        [ sg.Text("Match Statistics Menu") ],
        [ sg.Text(game.quarter_scorings())],
        [ sg.Text("")],
        [ sg.Text("                          "), sg.Text(game.home), sg.Text(game.away)],
        [ sg.Text("Longest drought"), sg.Text(drought[0]), sg.Text(drought[1])],
        [ sg.Text("Greatest partial"), sg.Text(partial[0]), sg.Text(partial[1])],
        [ sg.Text("Greatest streak"), sg.Text(streak[0]), sg.Text(streak[1])],
        [ sg.Text("")],
        [ sg.Button('Back to analyse match menu')]
    ]
    window = sg.Window("Match Statistics Menu", layout)
    event, values = window.read()

    if event == 'Back to analyse match menu':
        window.close()
        analyseMatch(game)


def analyseMatch(game):
    window = analyseMatchMenu()
    event, values = window.read()

    if event == 'Box scores':
        window.close()
        chooseBoxScore(game)
    if event == 'Match statistics':
        window.close()
        matchStatistics(game)
    elif event == 'Back to define match menu':
        window.close()
        defineMatch()


def defineMatch():
    window = defineMatchMenu()
    event, values = window.read()

    if event == 'OK':
        game = Match(values['Home'], values['Away'], values['Date'])
        window.close()
        analyseMatch(game)
    elif event == 'Back to main menu':
        window.close()
        main()


def main():
    window = mainMenu()
    event, values = window.read()

    if event == 'Analyse match':
        window.close()
        defineMatch()

if __name__ == '__main__':
    main()