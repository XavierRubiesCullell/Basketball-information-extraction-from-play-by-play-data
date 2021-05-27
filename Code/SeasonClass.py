import os
from bs4 import BeautifulSoup
import urllib.request
import altair as alt

from Functions import *
from StatisticEvolutionTable import main as StatisticEvolutionTable_main
from StatisticEvolutionPlot import main as StatisticEvolutionPlot_main

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

        # information retrieval:
        season = self.season.split("-")[1]
        webpage = f"https://www.basketball-reference.com/teams/{self.team}/{season}_games.html"
        response = urllib.request.urlopen(webpage)
        htmlDoc = response.read()
        soup = BeautifulSoup(htmlDoc, 'html.parser')
        self.matchList = soup.find_all('tr')
    

    def get_statistic_evolution_table(self, statistic, category=None, player=None):
        '''
        This function returns the table of the evolution of a statistic during the season
        - statistic: statistic that we want to study (string)
        - category: category we want to study in case the statistic is "box score" (string)
        - player: player we want to study in case the statistic is "box score" (string)
        '''
        return StatisticEvolutionTable_main(self.team, self.season, self.matchList, statistic, category, player)


    def save_statistic_evolution_table(self, table, name, extension='html', folder=None):
        '''
        This function saves the table 'table'. This function has the argument table instead of calling get_evolution_table.
        This is due to the fact that get_evolution_table can be very slow. In case we already executed, we can simply use the result
        sending it to this function instead of calling it once again
        - table: data table (pandas.DataFrame)
        - name: name we want for the file (string). The table will be saved in Team_Season_name
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
            raise NameError(f"Extension {extension} is not correct. It must be csv or html")


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


    def save_statistic_evolution_plot(self, plot, name):
        '''
        This function saves the plot 'plot' in FileDirectory/Seasons/seasonName:
        - plot: altair plot object (altair.vegalite.v4.api.LayerChart)
        - name: name we want for the file (string). The plot will be saved in Team_Season_name
        '''
        plot.save(self.path + self.seasonName + "_" + name + ".html")