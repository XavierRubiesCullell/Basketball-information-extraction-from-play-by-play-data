import pandas as pd

from MatchClass import Match


def treat_match(i, row, team, table):
    '''
    This function treats adds the result of a match to the table containing them
    - i: row number in the season table (integer)
    - row: row in the season table (pandas.Series)
    - team: name of the team (string)
    - table: table where the value of the match will be added (pandas.DataFrame)
    '''
    home, away, date = row.Home, row.Away, row.Date
    game = Match(home, away, date)
    result = game.result()
    table.loc[i, 'Home score'] = result[0]
    table.loc[i, 'Away score'] = result[1]
    if result[0] > result[1] and team == home or result[1] > result[0] and team == away:
        table.loc[i, 'W/L'] = "W"
    else:
        table.loc[i, 'W/L'] = "L"


def main(team, matchTable):
    '''
    This function creates the season results table
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    '''
    table = pd.DataFrame(columns=['Date', 'Home', 'Home score', 'Away score', 'Away', 'W/L'])
    table['Date'] = matchTable['Date']
    table['Home'] = matchTable['Home']
    table['Away'] = matchTable['Away']
    for i, row in matchTable.iterrows():
        treat_match(i, row, team, table)

    return table