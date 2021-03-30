import pandas as pd
import datetime
import os
import numpy as np

from Functions import *


class BoxScore():
    categories = ['Mins', '2PtI', '2PtA', '2Pt%', '3PtI', '3PtA', '3Pt%', 'FG%', '1PtI', '1PtA', '1Pt%', 'OR', 'DR', 'TR', '2PtAst', '3PtAst', 'Ast', 'Bl', 'St', 'To', 'FM', 'FR', 'AstPts', 'Pts', '+/-']

    def __init__(self, home, away, date, in_folder="Files/", in_file=None, start="48:00", end="0:00"):
        '''
        - home: name of the home team (string)
        - away: name of the visiting team (string)
        - date: date of the match (string)
        - in_folder: folder where the PbP file is (string)
        - in_file: name of the PbP file (string)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        self.home = home
        self.away = away
        self.date = date
        if in_file is None:
            in_file = home+away+date+"_StandardPbP.txt"
        self.file = in_folder + in_file
        self.start = start
        self.end = end
        
        # tables where the boxscore of the local and visiting team will be computed respectively
        self.table1 = pd.DataFrame(columns = BoxScore.categories).astype({'Mins': 'datetime64[ns]', '2Pt%': 'float'})
        self.table2 = pd.DataFrame(columns = BoxScore.categories).astype({'Mins': 'datetime64[ns]', '2Pt%': 'float'})

        # integers where the plusminus of the local and visiting team will be stored
        self.__plusminus1 = 0
        self.__plusminus2 = 0

        # dictionaries that will hold the local and visiting players respectively at a specific time
        self.__oncourt1 = {}
        self.__oncourt2 = {}

        # dictionaries that will hold the playing intervals of the local and visiting players respectively
        self.playerintervals1 = {}
        self.playerintervals2 = {}

        # list that will store the plays not used for the boxscore computation
        self.__others = []

        self.compute_box_score()


    def get_teams(self):
        return self.home, self.away

    def get_date(self):
        return self.date
    
    def get_interval(self):
        return self.start, self.end

    def get_file(self):
        return self.file

    def get_playerintervals(self):
        return self.playerintervals1, self.playerintervals2

    def get_tables(self):
        return self.table1, self.table2


    def compute_box_score(self):
        '''
        This function builds table1 and table2 and playerintervals1 and playerintervals2
        '''
        os.chdir(os.path.dirname(__file__))

        start = time_from_string(self.start)
        end = time_from_string(self.end)

        with open(self.file, encoding="utf-8") as f:
            self.__read_plays(f, start, end)

        self.__quarter_end(4, start, end)

        self.__final_computations()


    def __read_plays(self, f, start, end):
        '''
        This function launches the sequential analysis of sentences
        - f: file object with the PbP in the standard format
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        self.__Q = 1
        self.__lines = f.readlines()
        for i, line in enumerate(self.__lines):
            line = line.strip()
            self.__treat_line(i, line, start, end)


    def __treat_line(self, i, line, start, end):
        '''
        This function is launched to detect the type of play an action is
        - i: index of the studied line. It will be useful in plays such as free throws (int)
        - line: studied line (string)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        action = line.split(", ")
        
        #we need to check whether there was a change of quarter
        clock = action[0]
        clock = time_from_string(clock)
        prev_Q = self.__Q
        self.__Q = (4-int(clock.minute/12))
        if prev_Q != self.__Q:
            self.__quarter_end(prev_Q, start, end)
        
        # classification of the action
        if len(action) > 3 and action[3] == "S":
            self.__shoot(i, action, start, end)
        elif len(action) > 3 and action[3] == "R":
            self.__rebound(action, start, end)
        elif len(action) > 3 and action[3] == "T":
            self.__turnover(action, start, end)
        elif len(action) > 3 and action[3] == "St":
            self.__steal(action, start, end)
        elif len(action) > 3 and action[3] == "B":
            self.__block(action, start, end)
        elif len(action) > 3 and action[3] == "F":
            self.__foul(action, start, end)
        elif len(action) > 3 and action[3] == "C":
            self.__change(action, start, end)
        else:
            if start >= clock and clock >= end:
                self.__others.append(action)

    
    def __quarter_end(self, Q, start, end):
        '''
        This function is launched every time a quarter end is detected
        - Q: quarter that has just ended (int)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        # we add the minutes of the players that end the quarter (as it is usually done when they are changed)
        for player in self.__oncourt1:
            interval, int_min, int_max = compute_interval(self.__oncourt1[player], datetime.time(0, 12*(4-Q), 0), start, end)
            if interval != datetime.timedelta():
                self.__check_player("1", player)
                self.__modify_table("1", player, 'Mins', interval)
                if player not in self.playerintervals1.keys():
                    self.playerintervals1[player] = []
                self.playerintervals1[player].append((int_min.strftime("%M:%S"), int_max.strftime("%M:%S")))

        for player in self.__oncourt2:
            interval, int_min, int_max = compute_interval(self.__oncourt2[player], datetime.time(0, 12*(4-Q), 0), start, end)
            if interval != datetime.timedelta():
                self.__check_player("2", player)
                self.__modify_table("2", player, 'Mins', interval)
                if player not in self.playerintervals2.keys():
                    self.playerintervals2[player] = []
                self.playerintervals2[player].append((int_min.strftime("%M:%S"), int_max.strftime("%M:%S")))

        # we delete the variables related to the quarter
        self.__plusminus1 = 0
        self.__plusminus2 = 0
        self.__oncourt1.clear()
        self.__oncourt2.clear()


    def __final_computations(self):
        '''
        This function computes the cumulative value for every category and computes the dependent categories
        '''
        # computation of the cumulative values:
        self.table1.loc["TOTAL"] = self.table1.apply(np.sum)
        self.table2.loc["TOTAL"] = self.table2.apply(np.sum)

        # computation of the dependent categories:
        for pl, row in self.table1.iterrows():
            # computation of 1Pt%, 2Pt% and 3Pt%:
            for i in range(1,4):
                if row[str(i)+'PtA'] != 0:
                    perc = row[str(i)+'PtI']/row[str(i)+'PtA'] * 100
                    self.table1.loc[pl,str(i)+'Pt%'] = round(perc, 2)
                else:
                    self.table1.loc[pl,str(i)+'Pt%'] = "-"
            # computation of field goal percentage (FG%):
            if row['2PtA'] + row['3PtA'] != 0:
                perc = (row['2PtI'] + row['3PtI'])/(row['2PtA'] + row['3PtA']) * 100
                self.table1.loc[pl,'FG%'] = round(perc, 2)
            else:
                self.table1.loc[pl,'FG%'] = "-"


    def __shoot(self, i, action, start, end):
        '''
        Treatment of an action that was detected as a shot. It will have the following structure:
         clock team player "S" points [dist] result [A assistant]
        - i: index of the studied line. It will be useful in plays such as free throws (int)
        - action: studied play (list)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        clock, team, player, points = action[0], action[1], action[2], action[4]
        clock = time_from_string(clock)
        op_team = str((int(team)*5)%3)  # team = 1 -> op_team = 2, team = 2 -> op_team = 1
        self.__check_oncourt(team, player, clock, start, end)

        if start >= clock and clock >= end:
            self.__check_player(team, player)
            self.__modify_table(team, player, points+"PtA", 1)
        dist_given = action[5] != "I" and action[5] != "O" # true if it is not I or O, so in this position we have the distance
        
        result = action[5 + dist_given]
        if result == "I": # the shot was in
            if start >= clock and clock >= end:
                self.__modify_table(team, player, points+"PtI", 1)
                self.__modify_table(team, player, 'Pts', int(points))
                vars(self)["_BoxScore__plusminus"+team] += int(points)
                for pl in vars(self)["_BoxScore__oncourt"+team]: #modificacion of the +/- of the scoring team
                    self.__check_player(team, pl)
                    self.__modify_table(team, pl, '+/-', int(points))
                vars(self)["_BoxScore__plusminus"+op_team] -= int(points)
                for pl in vars(self)["_BoxScore__oncourt"+op_team]: #modificacion of the +/- of the opposite team
                    self.__check_player(op_team, pl)
                    self.__modify_table(op_team, pl, '+/-', -int(points))
                
                if points == "1": # we must check whether there was a miscalculation of +/-
                    self.__correct_plusminus(i)

            if len(action) == 8+dist_given and action[6+dist_given] == "A": # there is an assist
                assistant = action[7+dist_given]
                self.__check_oncourt(team, assistant, clock, start, end)
                if start >= clock and clock >= end:
                    self.__check_player(team, assistant)
                    self.__modify_table(team, assistant, 'Ast', 1)
                    self.__modify_table(team, assistant, points+'PtAst', 1)
                    self.__modify_table(team, player, 'AstPts', int(points))


    def __rebound(self, action, start, end):
        '''
        Treatment of an action that was detected as a rebound. It will have the following structure:
         clock team player "R" kind
        - action: studied play (list)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        clock, team, player, kind = action[0], action[1], action[2], action[4]
        clock = time_from_string(clock)
        self.__check_oncourt(team, player, clock, start, end)

        if start >= clock and clock >= end:
            self.__check_player(team, player)
            self.__modify_table(team, player, 'TR', 1)
            self.__modify_table(team, player, kind+"R", 1)


    def __turnover(self, action, start, end):
        '''
        Treatment of an action that was detected as a simple turnover. It will have the following structure:
         clock team player "T"
        - action: studied play (list)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        clock, team, player = action[0], action[1], action[2]
        clock = time_from_string(clock)
        self.__check_oncourt(team, player, clock, start, end)

        if start >= clock and clock >= end:
            self.__check_player(team, player)
            self.__modify_table(team, player, 'To', 1)


    def __steal(self, action, start, end):
        '''
        Treatment of an action that was detected as a steal. It will have the following structure:
         clock team player "St" receiver
        - action: studied play (list)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        clock, team, player, op_player = action[0], action[1], action[2], action[4]
        clock = time_from_string(clock)
        self.__check_oncourt(team, player, clock, start, end)
        op_team = str((int(team)*5)%3)  # team = 1 -> op_team = 2, team = 2 -> op_team = 1
        self.__check_oncourt(op_team, op_player, clock, start, end)

        if start >= clock and clock >= end:
            self.__check_player(team, player)
            self.__modify_table(team, player, 'St', 1)
            self.__check_player(op_team, op_player)
            self.__modify_table(op_team, op_player, 'To', 1)


    def __block(self, action, start, end):
        '''
        Treatment of an action that was detected as a block. It will have the following structure:
         clock team player "B" receiver points
        - action: studied play (list)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        clock, team, player, op_player, points = action[0], action[1], action[2], action[4], action[5]
        clock = time_from_string(clock)
        self.__check_oncourt(team, player, clock, start, end)
        
        op_team = str((int(team)*5)%3)  # team == 1 -> op_team = 2,  team == 2 -> op_team = 1
        self.__check_oncourt(op_team, op_player, clock, start, end)
        
        if start >= clock and clock >= end:
            self.__check_player(team, player)
            self.__modify_table(team, player, 'Bl', 1)
            self.__check_player(op_team, op_player)
            self.__modify_table(op_team, op_player, points+"PtA", 1)


    def __foul(self, action, start, end):
        '''
        Treatment of an action that was detected as a foul. It will have the following structure:
         clock team player "F" kind [receiver]
        - action: studied play (list)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        clock, team, player, kind = action[0], action[1], action[2], action[4]
        clock = time_from_string(clock)
        self.__check_oncourt(team, player, clock, start, end)
        
        if start >= clock and clock >= end:
            self.__check_player(team, player)
            self.__modify_table(team, player, 'FM', 1)
            if kind == "O":
                self.__modify_table(team, player, 'To', 1)

        if len(action) == 6: # there is a player from the opposite team that receives the foul
            op_player = action[5]
            op_team = str((int(team)*5)%3)
            self.__check_oncourt(op_team, op_player, clock, start, end)
            if start >= clock and clock >= end:
                self.__check_player(op_team, op_player)
                self.__modify_table(op_team, op_player, 'FR', 1)


    def __change(self, action, start, end):
        '''
        Treatment of an action that was detected as a change. It will have the following structure:
         clock team playerOut "C" playerIn
        - action: studied play (list)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        clock, team, playerOut, playerIn = action[0], action[1], action[2], action[4]
        clock = time_from_string(clock)
        self.__check_oncourt(team, playerOut, clock, start, end)

        interval, int_min, int_max = compute_interval(vars(self)["_BoxScore__oncourt"+team][playerOut], clock, start, end)
        if interval != datetime.timedelta(): # if it is equal, the interval is null (there is no overlap)
            self.__check_player(team, playerOut)
            self.__modify_table(team, playerOut, 'Mins', interval)
            self.__check_player(team, playerIn)
            if playerOut not in vars(self)["playerintervals"+team].keys():
                vars(self)["playerintervals"+team][playerOut] = []
            vars(self)["playerintervals"+team][playerOut].append((int_min.strftime("%M:%S"), int_max.strftime("%M:%S")))
        del vars(self)["_BoxScore__oncourt"+team][playerOut]
        vars(self)["_BoxScore__oncourt"+team][playerIn] = clock


    def __correct_plusminus(self, i):
        '''
        This function is launched when there is a scored free throw,
        to check whether there was a change after the corresponding foul.
        In case there was any change, it corrects the +/- of the involving players
        - i: the index of the free throw action (int)
        '''
        ft_action = self.__lines[i].strip().split(", ")
        j = i - 1
        action = self.__lines[j].strip().split(", ")
        while not (len(action) > 3 and action[3] == "F"): # we determine whether the action is a foul
            if len(action) > 3 and action[3] == "C": # we determine whether the action is a change
                team, playerOut, playerIn = action[1], action[2], action[4]
                points = 2*(team==ft_action[1]) - 1  #true -> 1, false -> -1
                self.__modify_table(team, playerOut, '+/-', points)
                self.__modify_table(team, playerIn, '+/-', -points)
            j -= 1
            action = self.__lines[j].strip().split(", ")


    def __check_player(self, team, player):
        '''
        This function is launched to avoid an error due to a missing key (player) in a boxscore table
        - team: team of the player, either 1 or 2 (string)
        - player: name of the player (string)
        '''
        if player not in set(vars(self)["table"+team].index):
            new_row = [datetime.timedelta()] + [0]*(len(BoxScore.categories)-1)
            new_row = pd.Series(new_row, index=BoxScore.categories, name=player)
            vars(self)["table"+team] = vars(self)["table"+team].append(new_row)


    def __check_oncourt(self, team, player, clock, start, end):
        '''
        This function is launched to check whether the presence of the player was already detected. In
        case it was not, it adds it to the players on court and adds the player +/- missing
        - team: team of the player, either 1 or 2 (string)
        - player: name of the player (string)
        - clock: time of a specific moment (string)
        - start: starting time of the boxscore compution interval (string)
        - end: ending time of the boxscore compution interval (string)
        '''
        if player != "-" and player not in vars(self)["_BoxScore__oncourt"+team]:
            vars(self)["_BoxScore__oncourt"+team][player] = datetime.time(0, (5-self.__Q)*12, 0)
            if start >= clock and clock >= end:
                self.__check_player(team, player)
                self.__modify_table(team, player, '+/-', vars(self)["_BoxScore__plusminus"+team])


    def __modify_table(self, team, player, variable, value):
        '''
        This function is launched to modify the boxscore values
        '''
        vars(self)["table"+team].loc[player,variable] += value