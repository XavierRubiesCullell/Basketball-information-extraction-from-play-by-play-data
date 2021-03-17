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

    def box_score_obtention(self):
        self.boxscore = BoxScore(self.home, self.away, self.date)
    
    def box_score_save(self, folder="Files/", pkl1 = None, pkl2 = None):
        if pkl1 is None:
            pkl1 = self.home+self.away+self.date+"_BS_"+self.home+".pkl"
        if pkl2 is None:
            pkl2 = self.home+self.away+self.date+"_BS_"+self.away+".pkl"
        if not "boxscore" in vars(self):
            self.box_score_obtention()
        self.boxscore.table1.to_pickle(folder + pkl1)
        self.boxscore.table2.to_pickle(folder + pkl2)


