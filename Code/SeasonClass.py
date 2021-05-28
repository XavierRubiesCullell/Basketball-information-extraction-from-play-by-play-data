import os
from bs4 import BeautifulSoup
import urllib.request
import altair as alt
import pandas as pd

from Functions import *
from StatisticEvolutionTable import main as StatisticEvolutionTable_main
from StatisticEvolutionPlot import main as StatisticEvolutionPlot_main
from ResultsTable import main as ResultsTable_main
from ResultsPlot import main as ResultsPlot_main

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
                row = pd.Series(row, index=["Date", "Home", "Away"])
                table = table.append(row, ignore_index=True)
    return table, round(playedNum/totalNum*100,2)


def matches_retrieval(team, season):
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


class Season():
    def __init__(self, team, season, fileFolder="Files/"):
        '''
        - team: name of the team. It can be the city, the club name or a combination (string)
        - season: season we are interested in (string)
        - fileFolder: directory where the Matches folder is/will be located (string)
        '''
        os.chdir(os.path.dirname(__file__))
        self.team = get_team(team)
        self.season = season
        self.seasonName = self.team + "_" + self.season
        path = os.getcwd()
        self.path = path + "/" + fileFolder + "Seasons/" + self.seasonName + "/"
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.matchTable, self.progress = matches_retrieval(self.team, self.season)
    
    def save_calendar(self, extension='html', folder=None):
        '''
        This function saves the calendar of the played matches of the season
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: directory where to save the plot (string)
        '''
        if folder is None:
            folder = self.path
        path = folder + self.seasonName + "_Calendar"
        if extension == 'csv':
            path += ".csv"
            self.matchTable.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            self.matchTable.to_html(path, encoding="utf8")
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")

    def get_results_table(self):
        '''
        This function creates the season results table
        '''
        return ResultsTable_main(self.team, self.matchTable)

    def save_results_table(self, extension='html', folder=None):
        '''
        This function saves the results of the played matches of the season
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: directory where to save the plot (string)
        '''
        if folder is None:
            folder = self.path
        path = folder + self.seasonName + "_ResultsTable"
        table = self.get_results_table()
        if extension == 'csv':
            path += ".csv"
            table.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            table.to_html(path, encoding="utf8")
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")

    def get_results_plot(self, plotId):
        '''
        This function creates the season results plot
        - plotId: Type of the plot we want:
          · 1: team
          · 2: opponent team
          · 3: both teams
          · 4: difference
        '''
        table = self.get_results_table()
        return ResultsPlot_main(self.team, self.season, table, plotId)

    def save_results_plot(self, plotId, folder=None):
        '''
        This function creates the season results plot
        - plotId: Type of the plot we want:
          · 1: team
          · 2: opponent team
          · 3: both teams
          · 4: difference
        - folder: directory where to save the plot (string)
        '''
        if folder is None:
            folder = self.path
        path = folder + self.seasonName + "_ResultsPlot"
        plot = self.get_results_plot(plotId)
        if plotId == 1:
            path += "Team"
        elif plotId == 2:
            path += "Opponent"
        elif plotId == 3:
            path += "Both"
        elif plotId == 4:
            path += "Difference"
        path += ".html"
        plot.save(path)

    def get_statistic_evolution_table(self, statistic, category=None, player=None):
        '''
        This function returns the table of the evolution of a statistic during the season
        - statistic: statistic that we want to study (string)
        - category: category we want to study in case the statistic is "box score" (string)
        - player: player we want to study in case the statistic is "box score" (string)
        '''
        return StatisticEvolutionTable_main(self.team, self.matchTable, statistic, category, player)


    def save_statistic_evolution_table(self, table, name, extension='html', folder=None):
        '''
        This function saves the table 'table'. This function has the argument table instead of calling get_evolution_table.
        This is due to the fact that get_evolution_table can be very slow. In case we already executed, we can simply use the result
        sending it to this function instead of calling it once again
        - table: data table (pandas.DataFrame)
        - name: name we want for the file (string). The table will be saved in Team_Season_name
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: directory where to save the plot (string)
        '''
        if folder is None:
            folder = self.path
        path = folder + self.seasonName + "_" + name
        if extension == 'csv':
            path += ".csv"
            table.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            table.to_html(path, encoding="utf8")
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")


    def get_statistic_evolution_plot(self, statistic, category=None, player=None, table=None):
        '''
        This function returns the plot of the evolution of a statistic during the season
        - statistic: statistic that we want to plot, in order to use it as an axis name (string)
        - category: category we want to study in case the statistic is "box score" (string)
        - player: player we want to study in case the statistic is "box score" (string)
        - table: values we want to plat (pandas.DataFrame)
        '''
        if table is None:
            table = self.get_statistic_evolution_table(statistic, category, player)
        return StatisticEvolutionPlot_main(self.team, self.season, statistic, category, player, table)


    def save_statistic_evolution_plot(self, plot, name, folder=None):
        '''
        This function saves the plot 'plot' in FileDirectory/Seasons/seasonName:
        - plot: altair plot object (altair.vegalite.v4.api.LayerChart)
        - name: name we want for the file (string). The plot will be saved in Team_Season_name
        - folder: directory where to save the plot (string)
        '''
        if folder is None:
            folder = self.path
        path = folder + self.seasonName + "_" + name + ".html"
        plot.save(path)