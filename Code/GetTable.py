import os
import datetime
import pandas as pd
import altair as alt

from Functions import *
from MatchClass import *

def convert_date_season(date):
    '''
    This functions receives a date in format "weekday, month day, year" and returns it in format "YYYYMMDD"
    '''
    date = datetime.datetime.strptime(date, "%a, %b %d, %Y")
    return date.strftime("%Y/%m/%d")


def treat_drought(drought):
    '''
    This function converts the scoring drought to minutes
    '''
    hours, mins, seconds = drought.split(":")
    return round(int(mins) + int(seconds)/60, 1)


def get_value(game, statistic, team, category, player):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - game: match we are treating (Match instance)
    - statistic: statistic that we want to study (string)
    - category: category we want to study in case the statistic is boxscore (string)
    - player: player we want to study in case the statistic is boxscore (string)
    Output:
    - value of the corresponding match (integer/float)
    '''
    if statistic == "streak":
        return game.greatest_streak()[team]
    if statistic == "partial":
        return game.greatest_partial()[team]
    if statistic == "drought":
        value = game.longest_drought()[team]
        return treat_drought(value)
    if statistic == "box score":
        boxScore = game.box_scores()[team]
        value = game.filter_by_categories(boxScore, [category])
        if value is None:
            return None
        value = game.filter_by_players(value, [player])
        if value is None:
            return None
        return value.iloc[0,0]


def treat_match(row, team, table, statistic, category, player):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - row: row in the season table (bs4.element.Tag)
    - team: name of the team. It can be the city, the club name or a combination (string)
    - table: table where the value of the match will be added (pandas.DataFrame)
    - statistic: statistic that we want to study (string)
    - category: category we want to study in case the statistic is boxscore (string)
    - player: player we want to study in case the statistic is boxscore (string)
    Output:
    - table: table with the value added
    '''
    cols = row.find_all('td')
    if len(cols) == 14:
        date = cols[0].text
        played = cols[3].text == "Box Score"
        location = cols[4].text
        opTeam = cols[5].text

        if played:
            date = convert_date_season(date)
            isAway = (location == "@")
            if isAway:
                home = opTeam
                away = team
            else:
                home = team
                away = opTeam

            game = Match(home, away, date)
            value = get_value(game, statistic, isAway, category, player)
            row = [date, opTeam, value]
            row = pd.Series(row, index=["Date", "Opponent", "Value"])
            table = table.append(row, ignore_index=True)
    return table


def main(team, season, matchList, statistic, category=None, player=None):
    '''
    This function returns the information desired for all the matches of a team during a season
    - team: name of the team. It can be the city, the club name or a combination (string)
    - season: season that is going to be analyzed (string)
    - matchList: list of matches (BeautifulSoup object)
    - statistic: statistic that we want to study (string)
    - category: category we want to study in case the statistic is boxscore (string)
    - player: player we want to study in case the statistic is boxscore (string)
    '''
    if statistic == "box score" and player is None:
        player = "TOTAL"

    table = pd.DataFrame(columns=["Date", "Opponent", "Value"])
    for line in matchList:
        table = treat_match(line, team, table, statistic, category, player)

    return table