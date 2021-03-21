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
for pl in game.boxscore.get_playerintervals()[0]:
    print(pl, ":   ", game.boxscore.get_playerintervals()[0][pl], sep="")
print()
for pl in game.boxscore.get_playerintervals()[1]:
    print(pl, ":   ", game.boxscore.get_playerintervals()[1][pl], sep="")

print()
print(vars(game.boxscore).keys())

print()
print(game.top_players(5, 'both', 'Pts'))

table = game.boxscore.get_tables()[0]

print(table)

print(filter_by_players(table,["G. Dieng", "G. Allen"]))

print(filter_by_categories(table,["2ptI", "2ptA"]))

print(filter_by_value(table,[("2ptI", 2), ("2ptA", 5)]))