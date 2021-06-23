from SeasonClass import Season

team = "Memphis"
year = "2020-2021"
season = Season(team, year)



# Calendar and results:

season.save_calendar()

print(season.get_results_table())

season.save_results_table()

plot = season.get_results_plot(1)
plot.show()

season.save_results_plot(4)

print(season.record())



# Box score: 

table = season.box_score(2)
print(table)

season.save_box_score(table, "PG")


print("\n\nfilter_by_players")
players = table.index[:2]
print(season.filter_by_players(table, players))

print("\n\nfilter_by_categories")
print(season.filter_by_categories(table, ["2PtM", "2PtA"]))
print()
print(season.filter_by_categories(table, "shooting"))
print()
print(season.filter_by_categories(table, "simple"))

print("\n\nfilter_by_value")
print(season.filter_by_value(table, {"2PtM": 2, "2PtA": 5}))

print("\n\ntop_players")
print(season.top_players(table, ['Pts', 'TR'], n=5))




# Statistic evolution:

statistic = "greatest streak"
table = season.get_statistic_evolution_table(statistic, category=None, player=None)
print(table)

season.save_statistic_evolution_table(table, statistic)

plot = season.get_statistic_evolution_plot(statistic, table)

season.save_statistic_evolution_plot(plot, statistic)



# Shooting statistics:

print(season.get_shooting_table(1))

season.save_shooting_table(2)

plot = season.get_shooting_plot(1)

season.save_shooting_plot(1, plot=plot)


# Assist statistics:

assists = season.get_assist_matrix()
print(assists)

season.save_assist_matrix()

plot = season.get_assist_plot(assists)
plot.show()

season.save_assist_plot()
season.save_assist_plot(plot=plot)