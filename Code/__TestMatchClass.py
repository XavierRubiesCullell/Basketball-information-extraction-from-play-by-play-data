# from MatchClass import Match

# home = "Denver"
# away = "Dallas"
# date = "2021/01/07"
# game = Match(home, away, date)

# # Get last quarter
# print("\n\nget_lastQ")
# print(game.get_lastQ())



# # BOX SCORES

# print("\n\nbox_scores")

# table = game.get_box_scores(0)
# game.save_box_score(table, "joint", extension="html")
# print(table)

# tables = game.get_box_scores()
# print("\nHome team boxscore from BoxScores.py")
# print(tables[0])
# print("\nAway team boxscore from BoxScores.py")
# print(game.get_box_scores(2))

# print("\n\nfilter_by_players")
# players = table.index[:2]
# print(game.filter_by_players(table, players))

# print("\n\nfilter_by_categories")
# print(game.filter_by_categories(table, ["2PtM", "2PtA"]))
# print()
# print(game.filter_by_categories(table, "shooting"))
# print()
# print(game.filter_by_categories(table, "simple"))

# print("\n\nfilter_by_value")
# print(game.filter_by_value(table, {"2PtM": 2, "2PtA": 5}))

# print("\n\ntop_players")
# print(game.top_players(table, ['Pts', 'TR'], n=5))



# # MATCH STATISTICS

# print("\n\nquarter_scorings")
# print(game.quarter_scorings("3Q:10:01"))


# # Get result
# print("\n\nresult")
# print(game.result())

# # Get winner
# print("\n\nwinner")
# print(game.winner())

# print("\n\nscoring_difference")
# print(game.scoring_difference())

# print("\n\nscoring_drought")
# print(game.scoring_drought())

# print("\n\nscoring_partial")
# print(game.scoring_partial())

# print("\n\nscoring_streak")
# print(game.scoring_streak())

# print(game.match_statistics())
# print(game.match_statistics("1Q:09:03"))



# # PLAYING TIMES

# print("\n\nplaying_intervals")
# playerIntervals, oncourtIntervals = game.playing_intervals()
# for team in range(1,3):
#     print("\nTEAM", team)
# # Get player intervals
#     for pl in playerIntervals[team-1]:
#         print(pl, ":   ", playerIntervals[team-1][pl], sep="")

#     print()
# # Get five intervals
#     for interval in oncourtIntervals[team-1]:
#         print(interval, ":   ", oncourtIntervals[team-1][interval], sep="")

# # Get five on court
# print("\n\nfive_on_court")
# fives = game.five_on_court("1Q:03:53")
# for team in range(1,3):
#     if len(fives[team-1]) == 5:
#         print(fives[team-1])
#     else:
#         print(f'There was a change at that time. The previous team is {fives[team-1][0]} and the next one is {fives[team-1][1]}')

# # Get intervals of a player
# print("\n\nintervals of player")
# print(game.intervals_of_player(1, "M. Morris"))

# # Get intervals of a five
# print("\n\nintervals of five")
# five = list(oncourtIntervals[1].values())[0]
# print(game.intervals_of_five(2, five))



# # SHOOTING AND ASSIST STATISTICS

# print("\n\nshooting statistics")
# shotStats = game.get_shooting_table()
# print("home")
# print(shotStats[0])
# print("away")
# print(shotStats[1])

# game.save_shooting_table(1)
# game.save_shooting_table(2)

# plot = game.get_shooting_plot(1)
# plot.show()
# plot = game.get_shooting_plot(2)
# plot.show()

# game.save_shooting_plot(1)
# game.save_shooting_plot(2)

# print("\n\nassist_map")
# assists = game.get_assist_matrix()
# print("home")
# print(assists[0])
# print("away")
# print(assists[1])

# game.save_assist_matrix(1)
# game.save_assist_matrix(2, assists[1])

# plot = game.get_assist_plot(1, assists[0])
# plot.show()
# plot = game.get_assist_plot(2)
# plot.show()

# game.save_assist_plot(1)
# game.save_assist_plot(2, plot)



# # VISUAL PBP

# import PySimpleGUI as sg
# layout = [
#     [sg.Text(key="ActionText", size=(40,1))],
#     [sg.Image(key="ActionImage")],
#     [sg.Text("", size=(20,1), key="Clock"), sg.Text("", size=(10,1), key="Score")],
#     [sg.Button('Back to play-by-play menu')]
# ]
# window = sg.Window("Visual PbP",layout)
# game.visual_PbP(window)

# print("\n\nVisual PbP")
# game.visual_PbP()