from MatchClass import *

home = "Utah"
away = "Clippers"
date = "20210101"
game = Match(home, away, date)

game.box_score_obtention("48:00", "0:00")
game.box_score_save()
print("\nHome team boxscore")
print(game.boxscore.get_tables()[0])
print("\nAway team boxscore")
print(game.boxscore.get_tables()[1])
print("\nPlay intervals")
print()
for i in range(2):
    for pl in game.boxscore.get_playerintervals()[i]:
        print(pl, ":   ", game.boxscore.get_playerintervals()[i][pl], sep="")

print()
print(vars(game.boxscore).keys())

table = game.boxscore.get_tables()[0]

print(table)

players = table.index[:2]
print(game.filter_by_players(players, table))

print(game.filter_by_categories(["2PtI", "2PtA"], table))
print(game.filter_by_categories("simple", table))

print(game.filter_by_value([("2PtI", 2), ("2PtA", 5)], table))

print()
print(game.top_players(['Pts', 'TR'], n=5))

print()
print(game.partial_scoring(end="12:01"))

print()
print(game.longest_drought())

print()
print(game.greatest_streak())

print()
assists = game.assist_map()
print(assists[0])
print(assists[1])


playerintervals, oncourtintervals = game.playing_intervals()
for team in range(1,3):
    print("\nTEAM", team)
    for pl in playerintervals[team-1]:
        print(pl, ":   ", playerintervals[team-1][pl], sep="")

    print()

    for interval in oncourtintervals[team-1]:
        print(interval, ":   ", oncourtintervals[team-1][interval], sep="")
    print()