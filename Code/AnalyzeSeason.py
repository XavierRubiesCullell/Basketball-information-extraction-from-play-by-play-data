import os
from bs4 import BeautifulSoup
import urllib.request
import datetime
from Functions import *
from MatchClass import *


def convert_date_season(date):
    '''
    This functions receives a date in format "weekday, month day, year" and returns it in format "YYYYMMDD"
    '''
    date = datetime.datetime.strptime(date, "%a, %b %d, %Y")
    return date.strftime("%Y/%m/%d")


def treat_match(row, team, currentDate):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - row: row in the season table (bs4.element.Tag)
    - team: name of the team. It can be the city, the club name or a combination (string)
    - currentDate: date at the time of the query (string)
    '''
    cols = row.find_all('td')
    if len(cols) == 14:
        date = cols[0].text
        location = cols[4].text
        opTeam = cols[5].text

        date = convert_date_season(date)
        if location == "@":
            home = opTeam
            away = team
        else:
            home = team
            away = opTeam
        print(home, away, date, end =" ")
        if date < currentDate:
            print("IN")
            game = Match(home, away, date)
        else:
            print("OUT")


def main(team, season):
    '''
    This function explores all the matches of a team during a season
    - team: name of the team. It can be the city, the club name or a combination (string)
    - season: season that is going to be analyzed (string)
    '''
    os.chdir(os.path.dirname(__file__))

    currentDate = datetime.date.today().strftime("%Y/%m/%d")
    shortTeam = get_team(team)
    season = season.split("-")[1]
    webpage = f"https://www.basketball-reference.com/teams/{shortTeam}/{season}_games.html"

    response = urllib.request.urlopen(webpage)
    htmlDoc = response.read()
    soup = BeautifulSoup(htmlDoc, 'html.parser')
    res = soup.find_all('tr')
    
    for line in res:
        treat_match(line, team, currentDate)


main("Memphis", "2020-2021")