import os
import pandas as pd
from Functions import *

from StandardPbPObtention import main as StandardPbPObtention_main
from BoxScores import main as BoxScores_main
from QuarterScorings import main as QuarterScorings_main
from LongestDrought import main as LongestDrought_main
from GreatestPartial import main as GreatestPartial_main
from GreatestStreak import main as GreatestStreak_main
from AssistMap import main as AssistMap_main
from PlayingIntervals import main as PlayingIntervals_main
from FiveOnCourt import main as FiveOnCourt_main
from FivesIntervals import main as FivesIntervals_main


class Match():
    def __init__(self, home, away, date, PbPFolder="Files/", PbPFile=None):
        '''
        - home: name of the local team (string)
        - away: name of the visiting team (string)
        - date: date of the match (string in YYYYMMDD format)
        - PbPFolder: directory where the standard PbP file is/will be located (string)
        - PbPFile: name of the standard PbP file (string)
        '''
        os.chdir(os.path.dirname(__file__))
        self.home = get_team(home)
        self.away = get_team(away)
        self.date = date
        if PbPFile is None:
            PbPFile = self.home + "_" + self.away + "_" + self.date + "_StandardPbP.txt"
        self.PbPFile = PbPFolder+PbPFile
        if not os.path.exists(self.PbPFile):
            self.lastQ = StandardPbPObtention_main('https://www.basketball-reference.com/boxscores/pbp/'+date+'0'+self.home+'.html', outFile = self.PbPFile)
        # self.boxscore will probably be generated
    
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

    def box_scores(self, start="1Q:12:00", end=None):
        '''
        It returns self.boxscore (after creating it if needed)
        - start, end: time interval where we want the box score to be computed (string)
        Output: It returns the box scores of both teams (list of pandas.DataFrame)
        '''
        if end is None:
            end = self.get_lastQ()+":00:00"
        if "boxscore" not in vars(self):
            self.boxscore = BoxScores_main(self.PbPFile, start=start, end=end)
        return self.boxscore
    
    def box_score_save(self, folder="Files/", pkl1 = None, pkl2 = None):
        '''
        This function saves the box scores in self.boxscore
        - folder: relative path to the folder where the box scores will be saved (string)
        - pkl1: name of the home file (string)
        - pkl2: name of the away file (string)
        '''
        if pkl1 is None:
            pkl1 = self.home + "_" + self.away + "_" + self.date + "_BS_" + self.home + ".pkl"
        if pkl2 is None:
            pkl2 = self.home + "_" + self.away + "_" + self.date + "_BS_" + self.away + ".pkl"
        
        (table1, table2) = self.box_scores()
        table1.to_pickle(folder + pkl1)
        table2.to_pickle(folder + pkl2)

    def filter_by_players(self, players, table=None):
        '''
        This function filters the box score values of a list of players
        - players: list of players as they are represented on the table (list of strings)
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        Output: Box score filtered by the list of players
        '''
        if not isinstance(table, pd.DataFrame):
            tables = self.box_scores()
            if isinstance(table, str):
                if table == self.home:
                    table = tables[0]
                elif table == self.away:
                    table = tables[1]
            else:
                table = tables[0].append(tables[1])
        return table.loc[players,]

    def filter_by_categories(self, categories, table=None):
        '''
        This function filters the box score values of a list of categories
        - categories: list of categories or type of categories (list of strings or string)
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        Output: Box score filtered by the list of categories
        '''
        if not isinstance(table, pd.DataFrame):
            tables = self.box_scores()
            if isinstance(table, str):
                if table == self.home:
                    table = tables[0]
                elif table == self.away:
                    table = tables[1]
            else:
                table = tables[0].append(tables[1])

        if categories == "shooting":
            categories = ['2PtI', '2PtA', '2Pt%', '3PtI', '3PtA', '3Pt%', 'FG%', '1PtI', '1PtA', '1Pt%', 'AstPts', 'Pts']
        elif categories == "rebounding":
            categories = ['OR', 'DR', 'TR']
        elif categories == "simple":
            categories = ['Mins', 'Pts', 'TR', 'Ast', 'Bl', 'St', 'To', 'FM', '+/-']
        return table[categories]

    def filter_by_value(self, vars, table=None):
        '''
        This function filters the box score of the players surpassing the minimum values introduced
        - vars: list of lists having the form (category, value)
        - table: box score or a variation (pandas dataframe) or a reference to a team (string)
        Output: Box score filtered by the values of the categories introduced
        '''
        if not isinstance(table, pd.DataFrame):
            tables = self.box_scores()
            if isinstance(table, str):
                if table == self.home:
                    table = tables[0]
                elif table == self.away:
                    table = tables[1]
            else:
                table = tables[0].append(tables[1])

        if "TOTAL" in table.index:
            table = table.drop(index = ["TOTAL"])
        if "-" in table.index:
            table = table.drop(index = ["-"])
        for (cat, val) in vars:
            table = table.loc[table[cat] >= val]
        return table

    def top_players(self, var, n=None, table=None, max=False):
        '''
        This function returns the top n players having the maximum/minimum value in var
        - var: category(ies) we are interested in (string)
        - n: number of players (integer)
        - table: box score or a variation (pandas dataframe) or a reference to a box score (string)
        - max: bool stating if we want the maximum values (true) or the minimum ones (false)
        Output: Table (series) with the players and the category(ies) value
        '''
        if not isinstance(table, pd.DataFrame):
            tables = self.box_scores()
            if isinstance(table, str):
                if table == self.home:
                    table = tables[0]
                elif table == self.away:
                    table = tables[1]
            else:
                table = tables[0].append(tables[1])

        table = table[var]
        table = table.drop(["-", "TOTAL"])
        table = table.sort_values(by=var, ascending=max)
        if n is not None:
            table = table[:n]
        return table

    def quarter_scorings(self, end=None):
        '''
        This function returns the scoring at every quarter end until time reaches 'end'
        - end: stopping time to compute the scoring (string)
        Ouput: pandas.DataFrame
        '''
        if end is None:
            end = self.get_lastQ()+":00:00"
        return QuarterScorings_main(self.PbPFile, self.home, self.away, end)

    def longest_drought(self):
        '''
        This function returns the longest time for every team without scoring
        Ouput: list of strings
        '''
        return LongestDrought_main(self.PbPFile, self.get_lastQ())

    def greatest_partial(self):
        '''
        This function returns the greatest partial (consecutive points without the opponent scoring) for every team
        Ouput: list of integers
        '''
        return GreatestPartial_main(self.PbPFile)
    
    def greatest_streak(self):
        '''
        This function returns the maximum amount of consecutive points without missing for every team
        Ouput: list of integers
        '''
        return GreatestStreak_main(self.PbPFile)

    def assist_map(self):
        '''
        This function draws the assists between each team members
        Ouput: assist matrix (list of pandas.DataFrame). M[i][j] indicates the number of assists from player i to player j
        '''
        return AssistMap_main(self.PbPFile)
  
    def playing_intervals(self):
        '''
        This function returns the playing intervals for every player and the 5 on court for each interval
        Output:
        - playersintervals: playing intervals for every team member (list [dictionary of {string: list of tuples}])
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
        Ouput: list of the intervals (list: [(start, end)])
        '''
        return FivesIntervals_main(self.playing_intervals()[1][team], five)