from MatchClass import *

home = "Memphis"
away = "Cleveland"
date = "20210107"
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