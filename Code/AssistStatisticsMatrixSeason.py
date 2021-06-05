import pandas as pd

from MatchClass import Match


def treat_match(row, team, assistsMatrix):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - row: row in the season table (pandas.Series)
    - team: name of the team (string)
    - assistsMatrix: assist matrix (pandas.DataFrame)
    Output:
    - assistsMatrix: assistsMatrix once the statistics of the game related to row were added (pandas.DataFrame)
    '''
    home, away, date = row.Home, row.Away, row.Date
    game = Match(home, away, date)
    if team == home:
        assistsMatrix, _ = game.get_assist_matrix(assists = [assistsMatrix, pd.DataFrame(dtype=int)])
    if team == away:
        _, assistsMatrix = game.get_assist_matrix(assists = [pd.DataFrame(dtype=int), assistsMatrix])
    return assistsMatrix


def main(team, matchTable):
    '''
    This function returns the matrix with the assists along the season
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    '''
    assistsMatrix = pd.DataFrame(dtype=int)

    for row in matchTable.itertuples():
        assistsMatrix = treat_match(row, team, assistsMatrix)

    # assists[0] = assists[0].astype({'Shots made': 'int32', 'Shots attempted': 'int32'})
    # assists[1] = assists[1].astype({'Shots made': 'int32', 'Shots attempted': 'int32'})

    return assistsMatrix