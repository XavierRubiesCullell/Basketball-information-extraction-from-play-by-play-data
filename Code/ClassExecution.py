from MatchClass import *

home = "Denver"
away = "Dallas"
date = "20210107"
game = Match(home, away, date)

print("\n\nget_lastQ")
print(game.get_lastQ())
print("\n\nbox_scores")
tables = game.box_scores()
game.box_score_save()
print("\nHome team boxscore from BoxScores.py")
print(tables[0])

print("\nAway team boxscore from BoxScores.py")
print(tables[1])

table = game.boxscore[1]
# print(table)

print("\n\nfilter_by_players")
players = table.index[:2]
print(game.filter_by_players(players, table))

print("\n\nfilter_by_categories")
print(game.filter_by_categories(["2PtI", "2PtA"], table))
print(game.filter_by_categories("simple", table))

print("\n\nfilter_by_value")
print(game.filter_by_value([("2PtI", 2), ("2PtA", 5)], table))

print("\n\ntop_players")
print(game.top_players(['Pts', 'TR'], n=5))

print("\n\nquarter_scorings")
print(game.quarter_scorings("2Q:10:01"))

print("\n\nlongest_drought")
print(game.longest_drought())

print("\n\ngreatest_partial")
print(game.greatest_partial())

print("\n\ngreatest_streak")
print(game.greatest_streak())

print("\n\nassist_map")
assists = game.assist_map()
print(assists[0])
print(assists[1])

print("\n\nplaying_intervals")
playerIntervals, oncourtIntervals = game.playing_intervals()
for team in range(1,3):
    print("\nTEAM", team)
    for pl in playerIntervals[team-1]:
        print(pl, ":   ", playerIntervals[team-1][pl], sep="")

    print()

    for interval in oncourtIntervals[team-1]:
        print(interval, ":   ", oncourtIntervals[team-1][interval], sep="")

print("\n\nfive_on_court")
fives = game.five_on_court("1Q:03:53")
for team in range(1,3):
    if len(fives[team-1]) == 5:
        print(fives[team-1])
    else:
        print(f'There was a change at that time. The previous team is {fives[team-1][0]} and the next one is {fives[team-1][1]}')


print("\n\nfives_intervals")
five = list(oncourtIntervals[1].values())[0]
print(game.fives_intervals(1, five))