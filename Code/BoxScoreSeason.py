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
        BS, _ = game.get_box_scores()
    elif team == away:
        _, BS = game.get_box_scores()

    BS['Mins'] = list(map(lambda x:to_timedelta(x), BS['Mins']))
    
    for player in BS.index:
        if player not in boxScore.index:
            boxScore.loc[player] = [0, datetime.timedelta()] + [0]*(len(categories)-1)

        boxScore.loc[player] += [1]+list(BS.loc[player, categories])

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


def main(team, matchTable, values=2):
    '''
    This function returns the box score for the team along the season
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    - values: it defines the box score wanted (integer) 1: total values, 2: values per game, 3: values per minute
    '''
    global categories
    categories = ['Mins', '2PtM', '2PtA', '3PtM', '3PtA', 'FGM', 'FGA', 'FTM', 'FTA', 'OR', 'DR', 'TR', 'Ast', 'PtsC', 'Bl', 'St', 'To', 'PF', 'DF', 'AstPts', 'Pts', '+/-']
    columns = ['GP'] + categories
    
    boxScore = pd.DataFrame(columns=columns).astype({'Mins': 'datetime64[ns]'})

    for row in matchTable.itertuples():
        boxScore = treat_match(row, team, boxScore)

    # normalisation:
    if values == 2:
        boxScore.columns.name = "Per game"
        GP = boxScore['GP']
        boxScore = boxScore.apply(lambda x: x/x.GP, axis=1)
        boxScore['EFF'] = EFF_computation(boxScore)
        boxScore['GP'] = GP
        boxScore['Mins'] = list(map(to_string, boxScore['Mins']))
    elif values == 3:
        boxScore.columns.name = "Per 36 minutes"
        GP = boxScore['GP']
        Mins = boxScore['Mins']
        boxScore = boxScore.apply(lambda x: x/(x.Mins.total_seconds()/60)*36, axis=1)
        boxScore['GP'] = GP
        boxScore['Mins'] = list(map(lambda x: int(x.total_seconds()/60), Mins))
    else:
        boxScore.columns.name = "Totals"
        boxScore['Mins'] = list(map(lambda x: int(x.total_seconds()/60), boxScore['Mins']))

    boxScore['FT%'] = boxScore.apply(lambda x: perc_computation(x['FTA'], x['FTM']), axis=1)
    boxScore['2Pt%'] = boxScore.apply(lambda x: perc_computation(x['2PtA'], x['2PtM']), axis=1)
    boxScore['3Pt%'] = boxScore.apply(lambda x: perc_computation(x['3PtA'], x['3PtM']), axis=1)
    boxScore['FGM'] = boxScore['2PtM'] + boxScore['3PtM']
    boxScore['FGA'] = boxScore['2PtA'] + boxScore['3PtA']
    boxScore['FG%'] = boxScore.apply(lambda x: perc_computation(x['FGA'], x['FGM']), axis=1)        

    boxScore = boxScore.round(1)
    # we sort the players:
    boxScore = boxScore.sort_values(by='Mins', ascending=False)
    total = boxScore.loc["TOTAL"]
    boxScore = boxScore.drop(index = ["TOTAL"], errors='ignore')
    boxScore.loc["TOTAL"] = total
    # we sort the columns:
    if values == 2:
        boxScore = boxScore[['GP', 'Mins', '2PtM', '2PtA', '2Pt%', '3PtM', '3PtA', '3Pt%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'OR', 'DR', 'TR', 'Ast', 'PtsC', 'Bl', 'St', 'To', 'PF', 'DF', 'AstPts', 'Pts', '+/-', 'EFF']]
    else:
        boxScore = boxScore[['GP', 'Mins', '2PtM', '2PtA', '2Pt%', '3PtM', '3PtA', '3Pt%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'OR', 'DR', 'TR', 'Ast', 'PtsC', 'Bl', 'St', 'To', 'PF', 'DF', 'AstPts', 'Pts', '+/-']]
    
    return boxScore