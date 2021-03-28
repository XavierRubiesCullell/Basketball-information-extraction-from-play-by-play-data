from StandardPbPObtention import StandardPbPObtentionMain
from BoxscoreObtention import BoxscoreObtentionMain

home = 'Memphis'
visiting = 'Cleveland'
date = '20210107'

StandardPbPObtentionMain('https://www.basketball-reference.com/boxscores/pbp/'+date+'0'+home[:3].upper()+'.html', out_file = home+visiting+date+"_StandardPbP.txt")
BoxscoreObtentionMain(in_file = home+visiting+date+"_StandardPbP.txt", pkl1 = home+visiting+date+"_BS_"+home+".pkl", pkl2 = home+visiting+date+"_BS_"+visiting+".pkl", start="48:00", end="0:00")