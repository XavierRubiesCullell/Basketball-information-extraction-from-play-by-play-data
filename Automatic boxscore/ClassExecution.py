from MatchClass import Match

home = "Memphis"
away = "Cleveland"
date = "20210107"
game = Match(home, away, date)

game.box_score_save()
print("\nHome team boxscore")
print(game.boxscore.table1)
print("\nAway team boxscore")
print(game.boxscore.table2)
print("\nPlay intervals")
for pl in game.boxscore.playintervals1:
    print(pl, ":   ", game.boxscore.playintervals1[pl], sep="")
print()
for pl in game.boxscore.playintervals2:
    print(pl, ":   ", game.boxscore.playintervals2[pl], sep="")

print()
print(vars(game.boxscore).keys())

print()
game.top_players('Pts', 33, 'both')