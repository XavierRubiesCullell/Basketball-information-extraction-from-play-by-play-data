import os

from StandardPbPObtention import StandardPbPObtentionMain
from BoxScoreClass import BoxScore
from PartialScorings import PartialScoringsMain
from LongestDrought import LongestDroughtMain
from GreatestStreak import GreatestStreakMain
from AssistMap import AssistMapMain
from PlayingIntervals import PlayingIntervalsMain



class Match():
    def __init__(self, home, away, date, PbPfile=None):
        os.chdir(os.path.dirname(__file__))
        self.home = home
        self.away = away
        self.date = date
        if PbPfile is None:
            PbPfile = home+away+date+"_StandardPbP.txt"
        self.PbPfile = PbPfile
        StandardPbPObtentionMain('https://www.basketball-reference.com/boxscores/pbp/'+date+'0'+home[:3].upper()+'.html', out_file = self.PbPfile)
        # self.boxscore will probably be generated, being an instance of BoxScore class

    def box_score_obtention(self, start="48:00", end="0:00"):
        '''
        It returns self.boxscore (after creating it if needed)
        Input:
        - start, end: time interval where we want the box score to be computed (string)
        Output: It returns the instance boxscore of class BoxScore
        '''
        if "boxscore" not in vars(self):
            self.boxscore = BoxScore(self.home, self.away, self.date, start=start, end=end)
        return self.boxscore
    
    def box_score_save(self, folder="Files/", pkl1 = None, pkl2 = None):
        '''
        This functions saves the box scores in self.boxscore (after creating it if needed)
        Input:
        - folder: relative path to the folder where the box scores will be saved (string)
        - pkl1: name of the home file (string)
        - pkl2: name of the away file (string)
        '''
        if pkl1 is None:
            pkl1 = self.home+self.away+self.date+"_BS_"+self.home+".pkl"
        if pkl2 is None:
            pkl2 = self.home+self.away+self.date+"_BS_"+self.away+".pkl"
        
        self.box_score_obtention()
        
        (table1, table2) = self.boxscore.get_tables()
        table1.to_pickle(folder + pkl1)
        table2.to_pickle(folder + pkl2)

    def filter_by_players(self, players, table=None):
        '''
        This function filters the box score values of a list of players
        Input:
        - players: list of players as they are represented on the table (list of strings)
        - table: box score or a variation (pandas dataframe) or a reference to a box score (string)
        Output: Box score filtered by the list of players
        '''
        if table is None:
            table = self.box_score_obtention().get_tables()[0].append(self.box_score_obtention().get_tables()[1])
        elif isinstance(table, str):
            if table == self.home:
                table = self.box_score_obtention().get_tables()[0]
            elif table == self.away:
                table = self.box_score_obtention().get_tables()[1]
        return table.loc[players,]

    def filter_by_categories(self, categories, table=None):
        '''
        This function filters the box score values of a list of categories
        Input:
        - categories: list of categories or type of categories (list of strings or string)
        - table: box score or a variation (pandas dataframe) or a reference to a box score (string)
        Output: Box score filtered by the list of categories
        '''
        if table is None:
            table = self.box_score_obtention().get_tables()[0].append(self.box_score_obtention().get_tables()[1])
        elif isinstance(table, str):
            if table == self.home:
                table = self.box_score_obtention().get_tables()[0]
            elif table == self.away:
                table = self.box_score_obtention().get_tables()[1]

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
        Input:
        - vars: list of lists having the form (category, value)
        - table: box score or a variation (pandas dataframe) or a reference to a box score (string)
        Output: Box score filtered by the values of the categories introduced
        '''
        if table is None:
            table = self.box_score_obtention().get_tables()[0].append(self.box_score_obtention().get_tables()[1])
        elif isinstance(table, str):
            if table == self.home:
                table = self.box_score_obtention().get_tables()[0]
            elif table == self.away:
                table = self.box_score_obtention().get_tables()[1]

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
        Input:
        - var: category(ies) we are interested in (string)
        - n: number of players (integer)
        - table: box score or a variation (pandas dataframe) or a reference to a box score (string)
        - max: bool stating if we want the maximum values (true) or the minimum ones (false)
        Output: Table (series) with the players and the category(ies) value
        '''
        if table is None:
            table = self.box_score_obtention().get_tables()[0].append(self.box_score_obtention().get_tables()[1])
        elif isinstance(table, str):
            if table == self.home:
                table = self.box_score_obtention().get_tables()[0]
            elif table == self.away:
                table = self.box_score_obtention().get_tables()[1]

        table = table[var]
        table = table.drop(["-", "TOTAL"])
        table = table.sort_values(by=var, ascending=max)
        if n is not None:
            table = table[:n]
        return table

    def partial_scoring(self, end="00:00"):
        '''
        This function returns the scoring at every quarter end
        '''
        return PartialScoringsMain("Files/"+self.PbPfile, self.home, self.away, end)

    def longest_drought(self):
        '''
        This function returns the longest time for every team without scoring
        '''
        return LongestDroughtMain("Files/"+self.PbPfile)

    def greatest_streak(self):
        '''
        This function returns the greatest scoring streak for every team
        '''
        return GreatestStreakMain("Files/"+self.PbPfile)

    def assist_map(self):
        '''
        This function draws the assists between each team members
        M[i][j] indicates the number of assists from player i to player j
        '''
        return AssistMapMain("Files/"+self.PbPfile)

  
    def playing_intervals(self):
        '''
        This function returns the playing intervals for every player and the 5 on court for each interval
        Output:
        - playersintervals: playing intervals for every team member (dictionary of string: list of tuples)
        - oncourtintervals: players on court for each interval without changes (dictionary of tuple: set of strings)
        '''
        return PlayingIntervalsMain("Files/" + self.PbPfile)