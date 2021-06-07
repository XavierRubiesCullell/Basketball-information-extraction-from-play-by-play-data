import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import datetime

from Functions import get_team

def convert_date_season(date):
    '''
    This functions receives a date in format "weekday, month day, year" and returns it in format "YYYYMMDD"
    '''
    date = datetime.datetime.strptime(date, "%a, %b %d, %Y")
    return date.strftime("%Y/%m/%d")

def treat_matches(team, matchList):
    '''
    This function treats all the matches in a season and checks whether they were played
    - team: name of the team (string)
    - matchList: web object with the matches (bs4.element.ResultSet)
    Output:
    - table: table with played matches
    - percentage: played percentage of the projected season
    '''
    table = pd.DataFrame(columns=['Date', 'Home', 'Away'])
    totalNum = 0
    playedNum = 0
    for row in matchList:
        cols = row.find_all('td')
        if len(cols) == 14:
            totalNum += 1
            date = cols[0].text
            played = cols[3].text == "Box Score"
            location = cols[4].text
            opTeam = get_team(cols[5].text)

            if played:
                playedNum += 1
                date = convert_date_season(date)
                teamIsAway = (location == "@")
                if teamIsAway:
                    home = opTeam
                    away = team
                else:
                    home = team
                    away = opTeam
                row = [date, home, away]
                row = pd.Series(row, index=["Date", "Home", "Away"], name=len(table)+1)
                table = table.append(row)
    return table, round(playedNum/totalNum*100,2)


def main(team, season):
    '''
    This function returns the played matches of a season of a team
    - team: short name of a team (string)
    - season: season name (string)
    '''
    season = season.split("-")[1]
    webpage = f"https://www.basketball-reference.com/teams/{team}/{season}_games.html"
    response = urllib.request.urlopen(webpage)
    htmlDoc = response.read()
    soup = BeautifulSoup(htmlDoc, 'html.parser')
    matchList = soup.find_all('tr')
    return treat_matches(team, matchList)