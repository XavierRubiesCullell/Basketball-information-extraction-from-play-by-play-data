import pandas as pd
import datetime
import math

from MatchClass import Match


def to_timedelta(duration):
    '''
    This functions converts an interval length as a string in HH:MM:SS format to timedelta
    - mins: interval length (string)
    '''
    duration = duration.split(":")
    duration = datetime.timedelta(hours = int(duration[0]), minutes = int(duration[1]), seconds = int(duration[2]))
    return duration

def to_string(duration):
    '''
    This functions converts an timedelta to a string in HH:MM:SS format
    - duration: interval length (string)
    '''
    duration = datetime.timedelta(seconds=math.ceil(duration.total_seconds()))
    return str(duration)


def treat_match(row, team, boxScore):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - row: row in the season table (pandas.Series)
    - team: name of the team (string)
    - boxScore: box score of the season (pandas.DataFrame)
    Output:
    - boxScore: updated box score of the season (pandas.DataFrame)
    '''
    home, away, date = row.Home, row.Away, row.Date
    game = Match(home, away, date)
    if team == home:
        BS, _ = game.box_scores()
    elif team == away:
        _, BS = game.box_scores()

    BS['Mins'] = list(map(lambda x:to_timedelta(x), BS['Mins']))
    
    for player in BS.index:
        if player not in boxScore.index:
            boxScore.loc[player] = [0, datetime.timedelta()] + [0]*(len(simpleCat)-1)

        boxScore.loc[player] += [1]+list(BS.loc[player, simpleCat])

    return boxScore


def perc_computation(att, made):
    '''
    This function computes the accuracy percentage in shooting statistics
    '''
    if att != 0:
        perc = made/att * 100
        return round(perc, 1)
    else:
        return "-"


def EFF_computation(box):
    '''
    This function computes the metric EFF of the boxscore per game
    '''
    effPos = box['Pts'] + box['TR'] + box['Ast'] + box['St'] + box['Bl']
    effNeg = (box['FGA'] - box['FGM']) + (box['FTA'] - box['FTM']) + box['To']
    return effPos - effNeg


def main(team, matchTable):
    '''
    This function returns the box score for the team along the season
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    '''
    global simpleCat
    simpleCat = ['Mins', '2PtM', '2PtA', '3PtM', '3PtA', 'FGM', 'FGA', 'FTM', 'FTA', 'OR', 'DR', 'TR', 'Ast', 'PtsC', 'Bl', 'St', 'To', 'PF', 'DF', 'AstPts', 'Pts', '+/-']
    columns = ['GP'] + simpleCat
    
    boxScore = pd.DataFrame(columns=columns).astype({'Mins': 'datetime64[ns]'})
    # boxScore.index.name = 'Player'

    for row in matchTable.itertuples():
        boxScore = treat_match(row, team, boxScore)

    GP = boxScore['GP']
    boxScore = boxScore.apply(lambda x: x/x.GP, axis=1)
    boxScore['Mins'] = list(map(to_string, boxScore['Mins']))        

    boxScore['FT%'] = boxScore.apply(lambda x: perc_computation(x['FTA'], x['FTM']), axis=1)
    boxScore['2Pt%'] = boxScore.apply(lambda x: perc_computation(x['2PtA'], x['2PtM']), axis=1)
    boxScore['3Pt%'] = boxScore.apply(lambda x: perc_computation(x['3PtA'], x['3PtM']), axis=1)
    boxScore['FGM'] = boxScore['2PtM'] + boxScore['3PtM']
    boxScore['FGA'] = boxScore['2PtA'] + boxScore['3PtA']
    boxScore['FG%'] = boxScore.apply(lambda x: perc_computation(x['FGA'], x['FGM']), axis=1)

    boxScore['GP'] = GP
    boxScore['EFF'] = EFF_computation(boxScore)

    boxScore = boxScore.round(1)
    boxScore = boxScore[['GP', 'Mins', '2PtM', '2PtA', '2Pt%', '3PtM', '3PtA', '3Pt%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'OR', 'DR', 'TR', 'Ast', 'PtsC', 'Bl', 'St', 'To', 'PF', 'DF', 'AstPts', 'Pts', '+/-', 'EFF']]
    boxScore = boxScore.sort_values(by='Mins', ascending=False)
    total = boxScore.loc["TOTAL"]
    boxScore = boxScore.drop(index = ["TOTAL"], errors='ignore')
    boxScore.loc["TOTAL"] = total
    
    return boxScore