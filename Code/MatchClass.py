from StandardPbPObtention import StandardPbPObtentionMain
from BoxScoreClass import BoxScore

import os

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
        # self.boxscore

    def box_score_obtention(self, start="48:00", end="0:00"):
        '''
        It returns self.boxscore (after creating it if needed)
        '''
        if "boxscore" not in vars(self):
            self.boxscore = BoxScore(self.home, self.away, self.date, start=start, end=end)
        return self.boxscore
    
    def box_score_save(self, folder="Files/", pkl1 = None, pkl2 = None):
        '''
        It saves the box scores in self.boxscore (after creating it if needed)
        '''
        if pkl1 is None:
            pkl1 = self.home+self.away+self.date+"_BS_"+self.home+".pkl"
        if pkl2 is None:
            pkl2 = self.home+self.away+self.date+"_BS_"+self.away+".pkl"
        
        self.box_score_obtention()
        
        (table1, table2) = self.boxscore.get_tables()
        table1.to_pickle(folder + pkl1)
        table2.to_pickle(folder + pkl2)

    def top_players(self, n, team, var, asc=False):
        '''
        This function returns the top n players having the maximum/minimum value in var
        '''
        self.box_score_obtention()
        if team == "1" or team == "home" or team == self.home:
            table = self.boxscore.get_tables()[0]
        elif team == "2" or team == "away" or team == self.away:
            table = self.boxscore.get_tables()[1]
        else:
            table = self.boxscore.get_tables()[0].append(self.boxscore.get_tables()[1])
        table = table[var]
        table = table.drop(["-", "TOTAL"])
        table = table.sort_values(ascending=asc)
        table = table[:n]
        return table

    def filter(self, team, vars):
        '''
        This function returns the box score of the players from team 'team' surpassing the minimum values established
        '''
        self.box_score_obtention()
        if team == "1" or team == "home" or team == self.home:
            table = self.boxscore.get_tables()[0]
        elif team == "2" or team == "away" or team == self.away:
            table = self.boxscore.get_tables()[1]
        else:
            table = self.boxscore.get_tables()[0].append(self.boxscore.get_tables()[1])
        print(vars)
        print(type(vars))
        table = table.drop(index = ["-", "TOTAL"])
        for (cat, val) in vars:
            table = table.loc[table[cat] >= val]
        return table