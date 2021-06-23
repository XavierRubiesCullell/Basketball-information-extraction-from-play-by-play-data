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
        shots1, shots0 = game.get_shooting_table(shots=[shots[1], shots[0]])
        shots = [shots0, shots1]
    return shots


def main(team, matchTable):
    '''
    This function returns the table with the shots for every distance from hoop for the team and the opponents
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    '''
    shots = [ pd.DataFrame(columns=['Distance (ft)', 'Points', 'Shots made', 'Shots attempted', 'Accuracy (%)', 'ExpPts']) ]*2

    for row in matchTable.itertuples():
        shots = treat_match(row, team, shots)

    for team in range(1,3):
        shots[team-1] = shots[team-1].sort_values(by=['Distance (ft)', 'Points'], ascending=True, ignore_index=True)
        shots[team-1].loc["TOTAL"] = shots[team-1].apply(sum)
        shots[team-1]['Accuracy (%)'] = round(shots[team-1]['Shots made']/shots[team-1]['Shots attempted']*100, 2)
        shots[team-1]['ExpPts'] = [x*y/100 for x,y in zip(shots[team-1]['Accuracy (%)'], shots[team-1]['Points'])]
        # arrangements for table visualisation:
        shots[team-1] = shots[team-1].round({'ExpPts': 2})
        shots[team-1] = shots[team-1].astype({'Distance (ft)': 'int32', 'Points': 'int32', 'Shots made': 'int32', 'Shots attempted': 'int32'})
        shots[team-1].loc["TOTAL", 'Distance (ft)'] = shots[team-1].loc["TOTAL", 'Points'] = shots[team-1].loc["TOTAL", 'ExpPts'] = "-"

    return shots