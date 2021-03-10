from StandardPbPObtention import StandardPbPObtentionMain
from BoxscoreObtention import BoxscoreObtentionMain

date = '20210107'
home = 'Memphis'
visiting = 'Cavaliers'

StandardPbPObtentionMain('https://www.basketball-reference.com/boxscores/pbp/'+date+'0'+home[:3].upper()+'.html', out_file = home+visiting+date+"_StandardPbP.txt")
BoxscoreObtentionMain(in_file = home+visiting+date+"_StandardPbP.txt", pkl1 = home+visiting+date+"_BS_"+home+".pkl", pkl2 = home+visiting+date+"_BS_"+visiting+".pkl", start="24:00", end="12:00")