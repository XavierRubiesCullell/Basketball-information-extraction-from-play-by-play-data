import os
import altair as alt
import pandas

from Functions import get_team
from MatchListObtention import main as MatchListObtention_main
from BoxScoreSeason import main as BoxScoreSeason_main
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
    team: str
    '''Short name of the team'''
    season: str
    '''Season year in YYYY-YYYY format'''
    seasonName: str
    '''Name of the season by the team, to be internally used'''
    matchTable: pandas.DataFrame
    '''Table with the played matches (pandas.DataFrame)'''
    progress: float
    '''Played percentage of the projected season (float)'''
    path: str
    '''Path where the outputs of the instance will be saved, in case no directory path is inputted when saving'''

    def __init__(self, team, season, path=None):
        '''
        - team: name of the team (string)
            - Location
            - Club name
            - The combination of the previous options <br>
        The third option is preferred, in order to avoid ambiguations in case the location/club name is not unique
        - season: season we are interested in (string). It must be from 1996-1997 season to present
        - path: directory where the output files will be saved:
            - String: Absolute path to an existing directory
            - None: Output files will be saved in ../Files/Seasons/self.seasonName  
                    In case it does not exist, it will be created
        '''
        self.team = get_team(team, season)
        self.season = season
        self.seasonName = self.team + "_" + self.season
        self.matchTable, self.progress = MatchListObtention_main(self.team, self.season)

        if path is None: # path will be ../Files/Seasons/self.seasonName
            os.chdir(os.path.dirname(__file__))
            currentPath = os.getcwd()
            fileDir = currentPath + "/../Files"
            if not os.path.isdir(fileDir):
                os.mkdir(fileDir)
            seasonsDir = fileDir + "/Seasons"
            if not os.path.isdir(seasonsDir):
                os.mkdir(seasonsDir)
            path = seasonsDir + "/"+ self.seasonName + "/"
            if not os.path.isdir(path):
                os.mkdir(path)
        self.path = path


    def save_calendar(self, extension='html', directory=None):
        '''
        This function saves the calendar of the played matches of the season
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - directory: directory where to save the calendar, in case self.path is not desired (string)
        '''
        if directory is None:
            directory = self.path
        path = directory + self.seasonName + "_Calendar"
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

        Output: pandas.DataFrame
        '''
        return ResultsTable_main(self.team, self.matchTable)


    def save_results_table(self, extension='html', directory=None):
        '''
        This function saves the results of the played matches of the season
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - directory: directory where to save the table, in case self.path is not desired (string)
        '''
        if directory is None:
            directory = self.path
        path = directory + self.seasonName + "_ResultsTable"
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
            - 1: team
            - 2: opponent team
            - 3: both teams
            - 4: difference

        Output: line chart (altair.vegalite.v4.api.LayerChart)
        '''
        table = self.get_results_table()
        return ResultsPlot_main(self.team, self.season, table, plotId)


    def save_results_plot(self, plotId, directory=None):
        '''
        This function creates the season results plot
        - plotId: Type of the plot we want:
            - 1: team
            - 2: opponent team
            - 3: both teams
            - 4: difference
        - directory: directory where to save the plot, in case self.path is not desired (string)
        '''
        if directory is None:
            directory = self.path
        path = directory + self.seasonName + "_ResultsPlot"
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

        Output: list
        '''
        record = [0, 0]
        for match in self.matchTable.itertuples():
            home, away, date = match.Home, match.Away, match.Date
            game = Match(home, away, date)
            record[game.winner() == self.team] += 1
        return [record[1], record[0]]


    def get_box_score(self, values=2):
        '''
        This function returns the season box score
        - values: it defines the box score wanted (integer):
            - 1: total values
            - 2: values per game
            - 3: values per minute

        Output: pandas.DataFrame
        '''
        return BoxScoreSeason_main(self.team, self.matchTable, values)


    def save_box_score(self, table, name="", extension='html', directory=None):
        '''
        This function saves the box score
        - table: box score (pandas.DataFrame)
        - name: name specification for the file (string)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - directory: directory where to save the box score, in case self.path is not desired (string)
        '''
        if directory is None:
            directory = self.path
        path = directory + self.seasonName + "_BS_" + name
        if extension == 'csv':
            path += ".csv"
            table.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            table.to_html(path, encoding="utf8")
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")


    def filter_by_players(self, table, players):
        '''
        This function filters the box score values of a list of players
        - table: box score or a variation (pandas dataframe)
        - players: list of players as they are represented on the table (list of strings)

        Output: Box score filtered by the list of players (pandas.DataFrame)
        '''
        for pl in players:
            if pl not in table.index:
                return None
        return table.loc[players,]


    def filter_by_categories(self, table, categories):
        '''
        This function filters the box score values of a list of categories
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        - categories: list of categories or type of categories (list of strings or string)

        Output: Box score filtered by the list of categories (pandas.DataFrame)
        '''
        if categories == "shooting":
            categories = ['2PtM', '2PtA', '2Pt%', '3PtM', '3PtA', '3Pt%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'AstPts', 'Pts']
        elif categories == "rebounding":
            categories = ['OR', 'DR', 'TR']
        elif categories == "simple":
            categories = ['GP', 'Mins', 'Pts', 'TR', 'Ast', 'Bl', 'St', 'To', 'PF', '+/-']
        for cat in categories:
            if cat not in table.columns:
                return None
        if 'Team' in table.columns:
            categories = ['Team'] + categories
        return table[categories]


    def filter_by_value(self, table, vars):
        '''
        This function filters the box score of the players surpassing the minimum values introduced
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        - vars: dictionary {category: value}

        Output: Box score filtered by the values of the categories introduced (pandas.DataFrame)
        '''
        table = table.drop(index = ["TOTAL"], errors='ignore')
        for cat, val in vars.items():
            if cat not in table.columns:
                return None
            table = table.loc[table[cat] >= val]
        return table


    def top_players(self, table, categories, n=None, max=True):
        '''
        This function returns the top n players having the maximum/minimum value in var
        - table: box score or a variation (pandas dataframe) or a reference to a box score (string)
        - categories: category(ies) we are interested in (list)
        - n: number of players (integer)
        - max: bool stating if we want the maximum values (true) or the minimum ones (false)

        Output: Table with the players and the category(ies) value (pandas.DataFrame)
        '''
        for cat in categories:
            if cat not in table.columns:
                return None
        table = table[categories]
        table = table.drop(index = ["TOTAL"], errors='ignore')
        table = table.sort_values(by=categories, ascending=not max)
        if n is not None:
            table = table[:n]
        return table


    def get_statistic_evolution_table(self, statistic, category=None, player=None):
        '''
        This function returns the table of the evolution of a statistic during the season
        - statistic: statistic that we want to study (string)
        - category: category we want to study in case the statistic is "box score" (string)
        - player: player we want to study in case the statistic is "box score" (string)

        Output: pandas.DataFrame
        '''
        return StatisticEvolutionTable_main(self.team, self.matchTable, statistic, category, player)


    def save_statistic_evolution_table(self, table, name, extension='html', directory=None):
        '''
        This function saves the table 'table'.
        It has the argument table instead of calling get_evolution_table.
        This is because get_evolution_table can be very slow. In case we already executed, 
        we can simply use the result sending it to this function instead of calling it once again
        - table: data table (pandas.DataFrame)
        - name: name we want for the file (string). The table will be saved in Team_Season_name
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - directory: directory where to save the table, in case self.path is not desired (string)
        '''
        if directory is None:
            directory = self.path
        path = directory + self.seasonName + "_" + name
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
        - category: category we want to study in case statistic is "box score" (string)
        - player: player we want to study in case statistic is "box score" (string)
        - table: values we want to plat (pandas.DataFrame)

        Output: line chart (altair.vegalite.v4.api.LayerChart)
        '''
        if table is None:
            table = self.get_statistic_evolution_table(statistic, category, player)
        return StatisticEvolutionPlot_main(self.team, self.season, statistic, category, player, table)


    def save_statistic_evolution_plot(self, plot, name, directory=None):
        '''
        This function saves the plot 'plot' in FileDirectory/Seasons/seasonName:
        - plot: altair plot object (altair.vegalite.v4.api.LayerChart)
        - name: name we want for the file (string). The plot will be saved in Team_Season_name
        - directory: directory where to save the plot, in case self.path is not desired (string)
        '''
        if directory is None:
            directory = self.path
        path = directory + self.seasonName + "_" + name + ".html"
        plot.save(path)


    def get_shooting_table(self, team=None):
        '''
        This function returns the table with the shots for every distance from hoop for the team and the opponents
        - team: team id (either 1: own or 2: opponents, integer) or None (both teams)

        Output: pandas.DataFrame or list of 2 pandas.DataFrame
        '''
        if team is None:
            return ShootingStatisticsTableSeason_main(self.team, self.matchTable)
        else:
            return ShootingStatisticsTableSeason_main(self.team, self.matchTable)[team-1]


    def save_shooting_table(self, team, table=None, extension='html', directory=None):
        '''
        This function saves the shooting statistics table of the desired team (either own or opponents)
        - team: team id (either 1: own or 2: opponents, integer)
        - table: table can be inputted in order to avoid recomputation (pandas.DataFrame)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - directory: directory where to save the table, in case self.path is not desired (string)
        '''
        if table is None:
            table = self.get_shooting_table(team)
        if directory is None:
            directory = self.path
        if team == 1:
            teamName = "own"
        else:
            teamName = "opponents"
        path = directory + self.seasonName + "_ShootingTable_" + teamName
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
        - team: team id (either 1: own, or 2: opponents, integer)
        - table: table can be inputted in order to avoid recomputation (pandas.DataFrame)

        Output: plotly.graph_objs._figure.Figure
        '''
        if table is None:
            table = self.get_shooting_table(team)
        return ShootingStatisticsPlot_main(table)


    def save_shooting_plot(self, team, plot=None, extension='svg', directory=None):
        '''
        This function saves the shooting statistics plot of the desired team (either own or opponents)
        - team: team id (either 1: own or 2: opponents, integer)
        - plot: plot can be inputted in order to avoid recomputation (plotly.graph_objs._figure.Figure)
        - extension: type of the file where the plot will be saved. It can be svg or pdf (vector), or png, jpeg or webp (raster)  (string)
        - directory: directory where to save the plot, in case self.path is not desired (string)
        '''
        if plot is None:
            plot = self.get_shooting_plot(team)
        if directory is None:
            directory = self.path
        if team == 1:
            teamName = "own"
        else:
            teamName = "opponents"
        if extension in ('svg', 'pdf', 'png', 'jpeg', 'webp'):
            path = directory + self.seasonName + "_ShootingPlot_" + teamName + "." + extension
            plot.write_image(path)
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be svg, pdf, png, jpeg or webp")


    def get_assist_matrix(self):
        '''
        This function returns the matrices describing the relation between passers and receivers

        Output: pandas.DataFrame
        '''
        return AssistStatisticsMatrixSeason_main(self.team, self.matchTable)


    def save_assist_matrix(self, matrix=None, extension='html', directory=None):
        '''
        This function saves the assist statistics matrix
        - matrix: matrix can be inputted in order to avoid recomputation (pandas.DataFrame)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - directory: directory where to save the matrix, in case self.path is not desired (string)
        '''
        if matrix is None:
            matrix = self.get_assist_matrix()
        if directory is None:
            directory = self.path
        path = directory + self.seasonName + "_AssistMatrix"
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

        Output: heatmap (altair.vegalite.v4.api.LayerChart)
        '''
        if matrix is None:
            matrix = self.get_assist_matrix()
        plot = AssistStatisticsPlot_main(matrix)
        return alt.layer(plot, title = self.team + " assists along the season " + self.season)


    def save_assist_plot(self, plot=None, directory=None):
        '''
        This function saves the assist statistics plot
        - plot: plot can be inputted in order to avoid recomputation (altair plot)
        - directory: directory where to save the plot, in case self.path is not desired (string)
        '''
        if plot is None:
            plot = self.get_assist_plot()
        if directory is None:
            directory = self.path

        path = directory + self.seasonName + "_AssistPlot.html"
        plot.save(path)