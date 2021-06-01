import pandas as pd

from MatchClass import Match


def treat_match(row, team, shots):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - row: row in the season table (pandas.Series)
    - team: name of the team (string)
    - shots: list of size 2 with the shooting tables, where the first one is for the team and the second one for the rivals (list of pandas.DataFrame)
    Output:
    - shots: updated list of size 2 with the shooting tables, where the first one is for the team and the second one for the rivals (list of pandas.DataFrame)
    '''
    home, away, date = row.Home, row.Away, row.Date
    game = Match(home, away, date)
    if team == home:
        shots = game.get_shooting_table(shots=shots)
    if team == away:
        shots = game.get_shooting_table(shots=[shots[1], shots[0]])


def main(team, matchTable):
    '''
    This function returns the information desired for all the matches of a team during a season
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    '''
    shots = [ pd.DataFrame(columns=['Shots made', 'Shots attempted', 'Accuracy (%)']) ]*2
    for iTeam in range(1,3):
        shots[iTeam-1] = shots[iTeam-1].astype({'Shots made': 'int32', 'Shots attempted': 'int32'})
        shots[iTeam-1].index.name = 'Distance (ft)'

    for row in matchTable.itertuples():
        treat_match(row, team, shots)

    shots[0] = shots[0].astype({'Shots made': 'int32', 'Shots attempted': 'int32'})
    shots[1] = shots[1].astype({'Shots made': 'int32', 'Shots attempted': 'int32'})

    return shots