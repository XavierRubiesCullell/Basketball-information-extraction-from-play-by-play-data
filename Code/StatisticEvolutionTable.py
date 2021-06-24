import pandas as pd

from MatchClass import Match

def treat_drought(drought):
    '''
    This function converts the scoring drought to minutes
    '''
    hours, mins, seconds = drought.split(":")
    return round(int(mins) + int(seconds)/60, 1)


def get_value(game, statistic, team, category, player):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - game: match we are treating (Match instance)
    - statistic: statistic that we want to study (string)
    - team: team id (integer)
    - category: category we want to study in case the statistic is boxscore (string)
    - player: player we want to study in case the statistic is boxscore (string)
    Output:
    - value of the corresponding match (integer/float)
    '''
    if statistic == "greatest difference":
        return game.scoring_difference()[team-1]
    if statistic == "greatest streak":
        return game.scoring_streak()[team-1]
    if statistic == "greatest partial":
        return game.scoring_partial()[team-1]
    if statistic == "longest drought":
        value = game.scoring_drought()[team-1]
        return treat_drought(value)
    if statistic == "box score":
        boxScore = game.get_box_scores()[team-1]
        value = game.filter_by_categories(boxScore, [category])
        if value is None:
            return None
        value = game.filter_by_players(value, [player])
        if value is None:
            return None
        return value.iloc[0,0]


def treat_match(row, team, table, statistic, category, player):
    '''
    This function treats all the matches in a season and does the desired computation for each of them
    - row: row in the season table (pandas.Series)
    - team: name of the team (string)
    - table: table where the value of the match will be added (pandas.DataFrame)
    - statistic: statistic that we want to study (string)
    - category: category we want to study in case the statistic is boxscore (string)
    - player: player we want to study in case the statistic is boxscore (string)
    Output:
    - table: table with the value added
    '''
    home, away, date = row.Home, row.Away, row.Date
    teamIsAway = team == away
    opTeam = (home, away)[not teamIsAway]
    game = Match(home, away, date)
    value = get_value(game, statistic, teamIsAway+1, category, player)
    row = [date, opTeam, value]
    row = pd.Series(row, index=["Date", "Opponent", "Value"])
    table = table.append(row, ignore_index=True)
    return table


def main(team, matchTable, statistic, category=None, player=None):
    '''
    This function returns the information desired for all the matches of a team during a season
    - team: name of the team (string)
    - matchTable: table of matches (pandas.DataFrame)
    - statistic: statistic that we want to study (string)
    - category: category we want to study in case the statistic is boxscore (string)
    - player: player we want to study in case the statistic is boxscore (string)
    '''
    if statistic == "box score" and player is None:
        player = "TOTAL"

    table = pd.DataFrame(columns=["Date", "Opponent", "Value"])
    for row in matchTable.itertuples():
        table = treat_match(row, team, table, statistic, category, player)

    return table