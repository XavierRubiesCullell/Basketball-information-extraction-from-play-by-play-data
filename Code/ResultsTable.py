import os
import datetime
import pandas as pd
import altair as alt

from Functions import *
from MatchClass import *


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


def main(team, matchTable):
    '''
    This function returns the information desired for all the matches of a team during a season
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    '''
    table = pd.DataFrame(columns=['Date', 'Home', 'Home score', 'Away score', 'Away'])
    table['Date'] = matchTable['Date']
    table['Home'] = matchTable['Home']
    table['Away'] = matchTable['Away']
    for i, row in matchTable.iterrows():
        treat_match(i, row, team, table)

    return table