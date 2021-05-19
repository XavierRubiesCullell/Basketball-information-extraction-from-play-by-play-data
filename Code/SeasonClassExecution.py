from SeasonClass import Season

team = "Memphis"
season = "2020-2021"
seasonObject = Season(team, season)


statistic = "streak"
table = seasonObject.get_info(statistic, category=None, player=None)
print(table)

plot = seasonObject.plot_line(table, statistic)

seasonObject.save_plot(plot, "Streak")