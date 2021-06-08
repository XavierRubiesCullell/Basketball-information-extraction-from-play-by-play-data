import os
import altair as alt

from Functions import get_team
from MatchListObtention import main as MatchListObtention_main
from StatisticEvolutionTable import main as StatisticEvolutionTable_main
from StatisticEvolutionPlot import main as StatisticEvolutionPlot_main
from ResultsTable import main as ResultsTable_main
from ResultsPlot import main as ResultsPlot_main
from ShootingStatisticsTableSeason import main as ShootingStatisticsTableSeason_main
from ShootingStatisticsPlot import main as ShootingStatisticsPlot_main
from AssistStatisticsMatrixSeason import main as AssistStatisticsMatrixSeason_main
from AssistStatisticsPlot import main as AssistStatisticsPlot_main

from MatchClass import Match


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
        self.matchTable, self.progress = MatchListObtention_main(self.team, self.season)
    
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

    def record(self):
        '''
        This function returns the W-L record of the season
        '''
        record = [0, 0]
        for match in self.matchTable.itertuples():
            home, away, date = match.Home, match.Away, match.Date
            game = Match(home, away, date)
            record[game.winner() == self.team] += 1
        return [record[1], record[0]]


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

    def get_shooting_table(self, team=None):
        '''
        This function returns the table with the shots for every distance from hoop for the team and the opponents
        - team: team id (either 1: own or 2: opponents, integer) or None
        Output: pandas.DataFrame or list of size 2 of pandas.DataFrame
        '''
        if team is None:
            return ShootingStatisticsTableSeason_main(self.team, self.matchTable)
        else:
            return ShootingStatisticsTableSeason_main(self.team, self.matchTable)[team-1]

    def save_shooting_table(self, team, table=None, extension='html', folder=None):
        '''
        This function saves the shooting statistics table of the desired team (either own or opponents)
        - team: team id (either 1: own or 2: opponents, integer)
        - table: table can be inputted in order to avoid recomputation (pandas.DataFrame)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: folder where the table will be saved (string)
        '''
        if table is None:
            table = self.get_shooting_table(team)
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = "own"
        else:
            teamName = "opponents"
        path = folder + self.seasonName + "_ShootingTable_" + teamName
        if extension == 'csv':
            path += ".csv"
            table.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            table.to_html(path, encoding="utf8")
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")

    def get_shooting_plot(self, team, table=None):
        '''
        This function returns the plot with the shots for every distance from hoop of the desired team (either own or opponents)
        - team: team id (either 1: own or 2: opponents, integer)
        - table: table can be inputted in order to avoid recomputation (pandas.DataFrame)
        Output: altair plot
        '''
        if table is None:
            table = self.get_shooting_table(team)
        return ShootingStatisticsPlot_main(table)

    def save_shooting_plot(self, team, plot=None, extension='svg', folder=None):
        '''
        This function saves the shooting statistics plot of the desired team (either own or opponents)
        - team: team id (either 1: own or 2: opponents, integer)
        - plot: plot can be inputted in order to avoid recomputation (plotly.graph_objs._figure.Figure)
        - extension: type of the file where the plot will be saved. It can be svg or pdf (vector), or png, jpeg or webp (raster)  (string)
        - folder: folder where the plot will be saved (string)
        '''
        if plot is None:
            plot = self.get_shooting_plot(team)
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = "own"
        else:
            teamName = "opponents"
        if extension in ('svg', 'pdf', 'png', 'jpeg', 'webp'):
            path = folder + self.seasonName + "_ShootingPlot_" + teamName + "." + extension
            plot.write_image(path)
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be svg, pdf, png, jpeg or webp")

    def get_assist_matrix(self):
        '''
        This function returns the matrices describing the relation between passers and receivers
        Output: pandas.DataFrame
        '''
        return AssistStatisticsMatrixSeason_main(self.team, self.matchTable)

    def save_assist_matrix(self, matrix=None, extension='html', folder=None):
        '''
        This function saves the assist statistics matrix
        - matrix: matrix can be inputted in order to avoid recomputation (pandas.DataFrame)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: folder where the table will be saved (string)
        '''
        if matrix is None:
            matrix = self.get_assist_matrix()
        if folder is None:
            folder = self.path
        path = folder + self.seasonName + "_AssistMatrix"
        if extension == 'csv':
            path += ".csv"
            matrix.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            matrix.to_html(path, encoding="utf8")
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")

    def get_assist_plot(self, matrix=None):
        '''
        This function returns the plot with the assist statistics
        - matrix: matrix can be inputted in order to avoid recomputation (pandas.DataFrame)
        '''
        if matrix is None:
            matrix = self.get_assist_matrix()
        plot = AssistStatisticsPlot_main(matrix)
        return alt.layer(plot, title = self.team + " assists along the season " + self.season)

    def save_assist_plot(self, plot=None, folder=None):
        '''
        This function saves the assist statistics plot
        - plot: plot can be inputted in order to avoid recomputation (altair plot)
        - folder: folder where the plot will be saved (string)
        '''
        if plot is None:
            plot = self.get_assist_plot()
        if folder is None:
            folder = self.path

        path = folder + self.seasonName + "_AssistPlot.html"
        plot.save(path)