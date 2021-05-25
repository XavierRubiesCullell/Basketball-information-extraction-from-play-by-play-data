import os
import pandas as pd
from Functions import *

from StandardPbPObtention import main as StandardPbPObtention_main
from BoxScores import main as BoxScores_main
from QuarterScorings import main as QuarterScorings_main
from GreatestDifference import main as GreatestDifference_main
from LongestDrought import main as LongestDrought_main
from GreatestPartial import main as GreatestPartial_main
from GreatestStreak import main as GreatestStreak_main
from ShootingStatisticsTable import main as ShootingStatisticsTable_main
from ShootingStatisticsPlot import main as ShootingStatisticsPlot_main
from AssistStatisticsMatrix import main as AssistStatisticsMatrix_main
from PlayingIntervals import main as PlayingIntervals_main
from FiveOnCourt import main as FiveOnCourt_main
from FivesIntervals import main as FivesIntervals_main
from VisualPbP import main as VisualPbP_main


def convert_date_match(date):
    '''
    This functions receives a date in format "YYYY/MM/DD" and returns it in format "YYYYMMDD"
    '''
    date = datetime.datetime.strptime(date, "%Y/%m/%d")
    return date.strftime("%Y%m%d")

class Match():
    def __init__(self, home, away, date, fileFolder="Files/"):
        '''
        - home: name of the local team. It can be the city, the club name or a combination (string)
        - away: name of the visiting team. It can be the city, the club name or a combination (string)
        - date: date of the match (string in YYYY/MM/DD format)
        - fileFolder: directory where the Matches folder is/will be located (string)
        '''
        os.chdir(os.path.dirname(__file__))
        self.home = get_team(home)
        self.away = get_team(away)
        self.date = date
        self.matchName = self.home + "_" + self.away + "_" + convert_date_match(self.date)
        path = os.getcwd()
        self.path = path + "/" + fileFolder + "Matches/" + self.matchName + "/"
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.PbPFile = self.path + "/" + self.matchName + "_StandardPbP.txt"
        if not os.path.exists(self.PbPFile):
            self.lastQ = StandardPbPObtention_main('https://www.basketball-reference.com/boxscores/pbp/'+convert_date_match(date)+'0'+self.home+'.html', outFile = self.PbPFile)
    
    def get_lastQ(self):
        '''
        This function returns the last quarter of the match (string)
        '''
        if "lastQ" not in vars(self):
            # the PbP file already existed, so we must compute lastQ
            with open(self.PbPFile, encoding="utf-8") as f:
                lines = f.readlines()
            lastLine = lines[-1]
            lastLine = lastLine.split(", ")
            clock = lastLine[0]
            self.lastQ = quarter_from_time(clock)
        return self.lastQ

    def box_scores(self, start=None, end=None, joint = False):
        '''
        It returns the box score of the interval introduced
        - start, end: time interval where we want the box score to be computed (string)
        Output: It returns the box scores of both teams (list of pandas.DataFrame)
        '''
        if start is None:
            start = "1Q:12:00"
        if end is None:
            end = self.get_lastQ()+":00:00"
        boxs = BoxScores_main(self.PbPFile, start=start, end=end)

        if not joint:
            return boxs
        boxs[0]['Team'] = [self.home]*len(boxs[0])
        boxs[1]['Team'] = [self.away]*len(boxs[1])
        table = boxs[0].append(boxs[1])
        return table[['Team'] + table.columns.tolist()[:-1]]
    
    def save_box_score(self, table, name="", extension='csv', folder=None):
        '''
        This function saves the box scores in a CSV
        - folder: relative path to the folder where the box score will be saved (string)
        - name: name specification for the file (string)
        '''
        if folder is None:
            folder = self.path
        path = folder + self.matchName + "_BS_" + name
        if extension == 'csv':
            path += ".csv"
            table.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            table.to_html(path, encoding="utf8")

    def filter_by_players(self, table, players):
        '''
        This function filters the box score values of a list of players
        - players: list of players as they are represented on the table (list of strings)
        - table: box score or a variation (pandas dataframe)
        Output: Box score filtered by the list of players
        '''
        for pl in players:
            if pl not in table.index:
                return None
        return table.loc[players,]

    def filter_by_categories(self, table, categories):
        '''
        This function filters the box score values of a list of categories
        - categories: list of categories or type of categories (list of strings or string)
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        Output: Box score filtered by the list of categories
        '''
        if categories == "shooting":
            categories = ['2PtM', '2PtA', '2Pt%', '3PtM', '3PtA', '3Pt%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'AstPts', 'Pts']
        elif categories == "rebounding":
            categories = ['OR', 'DR', 'TR']
        elif categories == "simple":
            categories = ['Mins', 'Pts', 'TR', 'Ast', 'Bl', 'St', 'To', 'PF', '+/-']
        for cat in categories:
            if cat not in table.columns:
                return None
        if 'Team' in table.columns:
            categories = ['Team'] + categories
        return table[categories]

    def filter_by_value(self, table, vars):
        '''
        This function filters the box score of the players surpassing the minimum values introduced
        - vars: dictionary {category: value}
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        Output: Box score filtered by the values of the categories introduced
        '''
        if "TOTAL" in table.index:
            table = table.drop(index = ["TOTAL"])
        for cat, val in vars.items():
            if cat not in table.columns:
                return None
            table = table.loc[table[cat] >= val]
        return table

    def top_players(self, table, categories, n=None, max=True):
        '''
        This function returns the top n players having the maximum/minimum value in var
        - var: category(ies) we are interested in (string)
        - n: number of players (integer)
        - table: box score or a variation (pandas dataframe) or a reference to a box score (string)
        - max: bool stating if we want the maximum values (true) or the minimum ones (false)
        Output: Table (series) with the players and the category(ies) value
        '''
        for cat in categories:
            if cat not in table.columns:
                return None
        table = table[categories]
        if "TOTAL" in table.index:
            table = table.drop(index = ["TOTAL"])
        table = table.sort_values(by=categories, ascending=not max)
        if n is not None:
            table = table[:n]
        return table

    def quarter_scorings(self, end=None):
        '''
        This function returns the scoring at each quarter end until time reaches 'end'
        - end: stopping time to compute the scoring (string)
        Output: pandas.DataFrame
        '''
        if end is None:
            end = self.get_lastQ()+":00:00"
        return QuarterScorings_main(self.PbPFile, self.home, self.away, end)

    def greatest_difference(self):
        '''
        This function returns the greatest difference in favour of each team
        Output: list of integers
        '''
        return GreatestDifference_main(self.PbPFile)

    def longest_drought(self):
        '''
        This function returns the longest time for each team without scoring
        Output: list of strings
        '''
        return LongestDrought_main(self.PbPFile, self.get_lastQ())

    def greatest_partial(self):
        '''
        This function returns the greatest partial (consecutive points without the opponent scoring) for each team
        Output: list of integers
        '''
        return GreatestPartial_main(self.PbPFile)
    
    def greatest_streak(self):
        '''
        This function returns the maximum amount of consecutive points without missing for each team
        Output: list of integers
        '''
        return GreatestStreak_main(self.PbPFile)

    def get_shooting_table(self, shots=None):
        '''
        This function returns the table with the shots for every distance from hoop for each team
        - shots: shooting table in case the shooting values are meant to be added to it (pandas.DataFrame)
        Output: list of pandas.DataFrame
        '''
        return ShootingStatisticsTable_main(self.PbPFile, shots)

    def save_shooting_table(self, team, extension='csv', folder=None):
        '''
        This function saves the shooting statistics table of the desired team
        - team: team id (integer)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: folder where the table will be saved (string)
        '''
        table = self.get_shooting_table()[team-1]
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away
        path = folder + self.matchName + "_shooting_table_" + teamName
        if extension == 'csv':
            path += ".csv"
            table.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            table.to_html(path, encoding="utf8")

    def get_shooting_plot(self, team):
        '''
        This function returns the plot with the shots for every distance from hoop for each team
        - team: team id (integer)
        '''
        shootingTables = self.get_shooting_table()
        return ShootingStatisticsPlot_main(shootingTables[team-1])
    
    def save_shooting_plot(self, team, extension='svg', folder=None):
        '''
        This function saves the shooting statistics plot of the desired team
        - team: team id (integer)
        - extension: type of the file where the plot will be saved. It can be svg or pdf (vector), or png, jpeg or webp (raster)  (string)
        - folder: folder where the plot will be saved (string)
        '''
        plot = self.get_shooting_plot(team)
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away
        if extension in ('svg', 'pdf', 'png', 'jpeg', 'webp'):
            path = folder + self.matchName + "_shooting_plot_" + teamName + "." + extension
            plot.write_image(path)

    def get_assist_matrix(self, assists=None):
        '''
        This function draws the assists between each team members
        - assists: shooting table in case the assist values are meant to be added to it (pandas.DataFrame)
        Output: assist matrix (list of pandas.DataFrame). M[i][j] indicates the number of assists from player i to player j
        '''
        return AssistStatisticsMatrix_main(self.PbPFile, assists)
    
    def save_assist_matrix(self, team, extension='csv', folder=None):
        '''
        This function saves the assist statistics matrix of the desired team
        - team: team id (integer)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: folder where the table will be saved (string)
        '''
        matrix = self.get_assist_matrix()[team-1]
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away
        path = folder + self.matchName + "_assist_matrix_" + teamName
        if extension == 'csv':
            path += ".csv"
            matrix.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            matrix.to_html(path, encoding="utf8")


    def playing_intervals(self):
        '''
        This function returns the playing intervals for each player and the 5 on court for each interval
        Output:
        - playersintervals: playing intervals for each team member (list [dictionary of {string: list of tuples}])
        - oncourtintervals: players on court for each interval without changes (list [dictionary of {tuple: set of strings}])
        '''
        return PlayingIntervals_main(self.PbPFile)
    
    def five_on_court(self, clock):
        '''
        This function returns the players on court at a given time
        - clock: timestamp (string)
        Output: either one five or two fives (list: [set or list of sets])
        '''
        return FiveOnCourt_main(self.playing_intervals()[1], clock)
    
    def fives_intervals(self, team, five):
        '''
        This function returns the intervals an introduced five played
        - team: players' team (integer)
        - five: list of players (list)
        Output: list of the intervals (list: [(start, end)])
        '''
        return FivesIntervals_main(self.playing_intervals()[1][team], five)
    
    def visual_PbP(self, window=None):
        '''
        This function executes the dynamic reproduction of the play-by-play
        - window: window in case we created a visual support (PySimpleGUI.PySimpleGUI.Window)
        '''
        return VisualPbP_main(self.PbPFile, self.get_lastQ(), window)