import os
from bs4 import BeautifulSoup
import urllib.request
import altair as alt

from Functions import *
from GetTable import main as GetTable_main

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
    
    def get_table(self, statistic, category=None, player=None):
        '''
        - statistic: statistic that we want to study (string)
        - category: category we want to study in case the statistic is boxscore (string)
        - player: player we want to study in case the statistic is boxscore (string)
        '''
        return GetTable_main(self.team, self.season, self.matchList, statistic, category, player)

    def plot_line(self, table, statistic):
        '''
        - table: values we want to plat (pandas.DataFrame)
        - statistic: statistic that we want to plot, in order to use it as an axis name (string)
        '''
        chart = alt.Chart(
            table.reset_index().dropna()
        ).mark_line(
            point=True
        ).encode(
            x = alt.X('index:T', title = "match"),
            y = alt.Y('Value:Q', title = "value"),
            tooltip = ['Date:T', 'Opponent:N']
        ).add_selection(
            alt.selection_single()
        )
        if statistic == "streak":
            statistic = "Greatest scoring streak"
        elif statistic == "partial":
            statistic = "Greatest partial"
        elif statistic == "drought":
            statistic = "Longest scoring drought"
        chart = alt.layer(chart, title = statistic + " along the " + self.season + "by" + self.team)

        rule = alt.Chart(table).mark_rule(color='darkblue').encode(
            y = alt.Y('mean(Value):Q')
        )
        return (chart + rule).properties(width=750)

    def save_plot(self, plot, name):
        '''
        This function saves the plot 'plot' in FileDirectory/Seasons/seasonName:
        - plot: altair plot object (altair.vegalite.v4.api.LayerChart)
        - name: name we want for the chart. Chart will be saved in (string)
        '''
        plot.save(self.path + self.seasonName + "_" + name + ".html")