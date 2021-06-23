import os
import pandas as pd
import altair as alt
import numpy as np

from Functions import *
from StandardPbPObtention import main as StandardPbPObtention_main
from BoxScores import main as BoxScores_main
from QuarterScorings import main as QuarterScorings_main
from ScoringDifference import main as ScoringDifference_main
from ScoringDrought import main as ScoringDrought_main
from ScoringPartial import main as ScoringPartial_main
from ScoringStreak import main as ScoringStreak_main
from ShootingStatisticsTable import main as ShootingStatisticsTable_main
from ShootingStatisticsPlot import main as ShootingStatisticsPlot_main
from AssistStatisticsMatrix import main as AssistStatisticsMatrix_main
from AssistStatisticsPlot import main as AssistStatisticsPlot_main
from PlayingIntervals import main as PlayingIntervals_main
from FiveOnCourt import main as FiveOnCourt_main
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
            try:
                self.lastQ = StandardPbPObtention_main('https://www.basketball-reference.com/boxscores/pbp/'+convert_date_match(date)+'0'+self.home+'.html', outFile = self.PbPFile)
            except:
                os.rmdir(self.path)
                raise Exception("Match does not exist")
    
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

    def box_scores(self, team = None, start=None, end=None):
        '''
        It returns the box score of the interval introduced
        - team: team id (None: both [list of tables], 0: joint table, 1: home, 2: away)
        - start, end: time interval where we want the box score to be computed (string)
        Output: It returns the box score of either one or both teams (pandas.DataFrame or list of pandas.DataFrame)
        '''
        if start is None:
            start = "1Q:12:00"
        if end is None:
            end = self.get_lastQ()+":00:00"
        boxs = BoxScores_main(self.PbPFile, start=start, end=end)

        if team is None:
            return boxs
        if team == 1 or team == 2:
            return boxs[team-1]
        boxs[0]['Team'] = [self.home]*len(boxs[0])
        boxs[1]['Team'] = [self.away]*len(boxs[1])
        table = boxs[0].append(boxs[1])
        return table[['Team'] + table.columns.tolist()[:-1]]
    
    def save_box_score(self, table, name="", extension='html', folder=None):
        '''
        This function saves the box score
        - table: box score (pandas.DataFrame)
        - name: name specification for the file (string)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: relative path to the folder where the box score will be saved (string)
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
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")

    def filter_by_players(self, table, players):
        '''
        This function filters the box score values of a list of players
        - table: box score or a variation (pandas dataframe)
        - players: list of players as they are represented on the table (list of strings)
        Output: Box score filtered by the list of players
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
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        - vars: dictionary {category: value}
        Output: Box score filtered by the values of the categories introduced
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
        Output: Table (series) with the players and the category(ies) value
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

    def quarter_scorings(self, end=None):
        '''
        This function returns the scoring at each quarter end until time reaches 'end'
        - end: stopping time to compute the scoring (string)
        Output: pandas.DataFrame
        '''
        if end is None:
            end = self.get_lastQ()+":00:00"
        return QuarterScorings_main(self.PbPFile, self.home, self.away, end)

    def result(self):
        '''
        This function returns the result of the match
        Output: list
        '''
        quarterScorings = self.quarter_scorings()
        finalScore = quarterScorings["T"]
        return finalScore.tolist()

    def winner(self, id=False):
        '''
        This function returns the winner of the match
        - id: Bool stating whether the id or the name of the winner is desired
        Output: either string (id=False) or integer (else)
        '''
        score = self.result()
        winner = np.argmax(score)+1
        if id:
            return winner
        return (self.home, self.away)[winner-1]

    def scoring_difference(self, timestamp=None):
        '''
        This function returns the greatest difference in favour of each team
        - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value along the match (string)
        Output: list of integers
        '''
        return ScoringDifference_main(self.PbPFile, timestamp)

    def scoring_partial(self, timestamp=None):
        '''
        This function returns the greatest partial (consecutive points without the opponent scoring) for each team
        - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value along the match (string)
        Output: list of integers
        '''
        return ScoringPartial_main(self.PbPFile, timestamp)
    
    def scoring_streak(self, timestamp=None):
        '''
        This function returns the maximum amount of consecutive points without missing for each team
        - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value along the match (string)
        Output: list of integers
        '''
        return ScoringStreak_main(self.PbPFile, timestamp)
    
    def scoring_drought(self, timestamp=None):
        '''
        This function returns the longest time for each team without scoring
        - timestamp: match timestamp in case a temporal value is wanted. None is for the greatest value along the match (string)
        Output: list of strings
        '''
        return ScoringDrought_main(self.PbPFile, self.get_lastQ(), timestamp)

    def match_statistics(self, timestamp=None):
        '''
        This function returns a table with the match statistics (difference, partial, streak and drought)
        Output: pandas.DataFrame
        '''
        table = pd.DataFrame(
            np.array((self.scoring_difference(timestamp),
                self.scoring_partial(timestamp),
                self.scoring_streak(timestamp),
                self.scoring_drought(timestamp) )), 
            columns = (self.home, self.away),
            index = ("Scoring difference", "Partial", "Scoring streak", "Scoring drought")
        )
        return table

    def get_shooting_table(self, team=None, shots=None):
        '''
        This function returns the table with the shots for every distance from hoop for each team
        - team: team id (either 1 or 2, integer)
        - shots: shooting table in case the shooting values are meant to be added to it (pandas.DataFrame)
        Output: list of pandas.DataFrame
        '''
        if team is None:
            return ShootingStatisticsTable_main(self.PbPFile, shots)
        else:
            return ShootingStatisticsTable_main(self.PbPFile, shots)[team-1]

    def save_shooting_table(self, team, table=None, extension='html', folder=None):
        '''
        This function saves the shooting statistics table of the desired team
        - team: team id (either 1 or 2, integer)
        - table: table can be inputted in order to avoid recomputation (pandas.DataFrame)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: folder where the table will be saved (string)
        '''
        if table is None:
            table = self.get_shooting_table(team)
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away
        path = folder + self.matchName + "_ShootingTable_" + teamName
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
        This function returns the plot with the shots for every distance from hoop of the desired team
        - team: team id (either 1 or 2, integer)
        - table: table can be inputted in order to avoid recomputation (pandas.DataFrame)
        '''
        if table is None:
            table = self.get_shooting_table(team)
        return ShootingStatisticsPlot_main(table)
    
    def save_shooting_plot(self, team, plot=None, extension='svg', folder=None):
        '''
        This function saves the shooting statistics plot of the desired team
        - team: team id (either 1 or 2, integer)
        - extension: type of the file where the plot will be saved. It can be svg or pdf (vector), or png, jpeg or webp (raster)  (string)
        - folder: folder where the plot will be saved (string)
        '''
        if plot is None:
            plot = self.get_shooting_plot(team)
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away
        if extension in ('svg', 'pdf', 'png', 'jpeg', 'webp'):
            path = folder + self.matchName + "_ShootingPlot_" + teamName + "." + extension
            plot.write_image(path)
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be svg, pdf, png, jpeg or webp")

    def get_assist_matrix(self, team=None, assists=None):
        '''
        This function draws the assists between each team members
        - team: team id (either 1 or 2, integer)
        - assists: assist table in case the assist values are meant to be added to it (pandas.DataFrame)
        Output: assist matrix (list of pandas.DataFrame). M[i][j] indicates the number of assists from player i to player j
        '''
        if team is None:
            return AssistStatisticsMatrix_main(self.PbPFile, assists)
        else:
            return AssistStatisticsMatrix_main(self.PbPFile, assists)[team-1]
    
    def save_assist_matrix(self, team, matrix=None, extension='html', folder=None):
        '''
        This function saves the assist statistics matrix of the desired team
        - team: team id (either 1 or 2, integer)
        - matrix: matrix can be inputted in order to avoid recomputation (pandas.DataFrame)
        - extension: type of the file where the table will be saved. It can either be csv or html (string)
        - folder: folder where the table will be saved (string)
        '''
        if matrix is None:
            matrix = self.get_assist_matrix(team)
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away
        path = folder + self.matchName + "_AssistMatrix_" + teamName
        if extension == 'csv':
            path += ".csv"
            matrix.to_csv(path, sep = ";", encoding="utf8")
        elif extension == 'html':
            path += ".html"
            matrix.to_html(path, encoding="utf8")
        else:
            raise ValueError(f"Extension {extension} is not correct. It must be csv or html")

    def get_assist_plot(self, team, matrix=None):
        '''
        This function returns the assist statistics plot of the desired team
        - team: team id (either 1 or 2, integer)
        - matrix: matrix can be inputted in order to avoid recomputation (pandas.DataFrame)
        Output: altair plot
        '''
        if matrix is None:
            matrix = self.get_assist_matrix(team)
        plot = AssistStatisticsPlot_main(matrix)
        
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away
        return alt.layer(plot, title = teamName + " assists")

    def save_assist_plot(self, team, plot=None, folder=None):
        '''
        This function saves the assist statistics plot of the desired team
        - team: team id (either 1 or 2, integer)
        - plot: plot can be inputted in order to avoid recomputation
        - folder: folder where the plot will be saved (string)
        '''
        if plot is None:
            plot = self.get_assist_plot(team)
        if folder is None:
            folder = self.path
        if team == 1:
            teamName = self.home
        else:
            teamName = self.away

        path = folder + self.matchName + "_AssistPlot_" + teamName + ".html"
        plot.save(path)

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

    def intervals_of_player(self, team, player):
        '''
        This function returns the intervals an introduced player played
        - team: five's team id (either 1 or 2, integer)
        - five: list of players (list)
        Output: list of the intervals (list: [(start, end)])
        '''
        playerIntervals = self.playing_intervals()[0][team-1]
        return playerIntervals.get(player, [])
    
    def intervals_of_five(self, team, five):
        '''
        This function returns the intervals an introduced five played
        - team: five's team id (either 1 or 2, integer)
        - five: list of players (list)
        Output: list of the intervals (list: [(start, end)])
        '''
        oncourtintervals = self.playing_intervals()[1][team-1]
        five = set(five)
        intervals = []
        for interval in oncourtintervals:
            if oncourtintervals[interval] == five:
                intervals.append(interval)
        return intervals
    
    def visual_PbP(self, window=False):
        '''
        This function executes the dynamic reproduction of the play-by-play
        - window: whether we want a visual support or console printing (bool)
        '''
        return VisualPbP_main(self.PbPFile, self.home, self.away, self.get_lastQ(), window)