from SeasonClass import Season

team = "Orlando"
season = "2020-2021"
seasonObject = Season(team, season)



# Calendar and results:

seasonObject.save_calendar()

print(seasonObject.get_results_table())

seasonObject.save_results_table()

plot = seasonObject.get_results_plot(1)
plot.show()

seasonObject.save_results_plot(4)

print(seasonObject.record())



# Box score: 

box = seasonObject.box_score(1)
print(box)

box = seasonObject.box_score(2)
path = "D:/Escola/3. Uni/Curs 2020-2021/2n quatrimestre/TFG/Code/Files/Seasons/ORL_2020-2021/BoxScore_PerGame.html"
box.to_html(path, encoding="utf8")



# Statistic evolution:

statistic = "greatest streak"
table = seasonObject.get_statistic_evolution_table(statistic, category=None, player=None)
print(table)

seasonObject.save_statistic_evolution_table(table, statistic)

plot = seasonObject.get_statistic_evolution_plot(statistic, table)

seasonObject.save_statistic_evolution_plot(plot, statistic)



Shooting statistics:

print(seasonObject.get_shooting_table(1))

seasonObject.save_shooting_table(2)

plot = seasonObject.get_shooting_plot(1)

seasonObject.save_shooting_plot(1, plot=plot)


# Assist statistics:

assists = seasonObject.get_assist_matrix()
print(assists)

seasonObject.save_assist_matrix()

plot = seasonObject.get_assist_plot(assists)
plot.show()

seasonObject.save_assist_plot()
seasonObject.save_assist_plot(plot=plot)