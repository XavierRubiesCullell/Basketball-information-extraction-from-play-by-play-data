from SeasonClass import Season

team = "Memphis"
season = "2020-2021"
seasonObject = Season(team, season)

seasonObject.save_calendar()

print(seasonObject.get_results_table())

seasonObject.save_results_table()

plot = seasonObject.get_results_plot(1)
plot.show()

seasonObject.save_results_plot(4)

statistic = "greatest streak"
table = seasonObject.get_statistic_evolution_table(statistic, category=None, player=None)
print(table)

seasonObject.save_statistic_evolution_table(table, statistic)

plot = seasonObject.get_statistic_evolution_plot(statistic, table)

seasonObject.save_statistic_evolution_plot(plot, statistic)