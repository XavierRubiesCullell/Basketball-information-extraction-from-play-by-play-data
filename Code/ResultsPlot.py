import pandas as pd
import altair as alt


def get_table(team, table):
    cols = ['Date', 'Opponent', 'TeamScore', 'OpponentScore', 'Difference', "Winner"]
    auxTable = pd.DataFrame(columns = cols)
    for match in table.itertuples():
        teamIsAway = team == match.Away
        opTeamIsAway = not teamIsAway
        opTeam = (match.Home, match.Away)[opTeamIsAway]
        difference = match[3+teamIsAway] - match[3+opTeamIsAway]
        row = [match.Date, opTeam, match[3+teamIsAway], match[3+opTeamIsAway], difference, difference>0]
        row = pd.Series(row, index = cols, name=len(auxTable)+1)
        auxTable = auxTable.append(row)
    return auxTable


def get_plot(table, variable, colors):
    if variable == 'Difference':
        yAxisTitle = "Difference"
    else:
        yAxisTitle = "Score"

    chart1 = alt.Chart(
        table.reset_index()
    ).mark_line(
        color = colors[0]
    ).encode(
        x = alt.X('index:O', title = "match"),
        y = alt.Y(variable+':Q', title = yAxisTitle)
    )
    
    chart2 = alt.Chart(
        table.reset_index()
    ).mark_circle(
        color = colors[0]
    ).encode(
        x = alt.X('index:O'),
        y = alt.Y(variable+':Q'),
        tooltip = ['Date:O', 'Opponent:N', alt.Tooltip(variable+':Q', title=yAxisTitle)]
    ).add_selection(
        alt.selection_single()
    )
    chart = chart1 + chart2

    rule = alt.Chart(
        table
    ).mark_rule(
        color=colors[1]
    ).encode(
        y = alt.Y('mean('+variable+'):Q')
    )
    return chart, rule


def main(team, season, table, plotId):
    '''
    This function creates the season results plot
    - team: team (string)
    - season: season (string)
    - plotId: Type of the plot we want:
        · 1: team
        · 2: opponent team
        · 3: both teams
        · 4: difference
    '''
    table = get_table(team, table)    
    
    if plotId == 1:
        plot, rule = get_plot(table, 'TeamScore', ["#4682b4", "darkblue"])
        chart = (plot + rule).properties(width=750)
        title = "Scoring along the " + season + " season by " + team

        chart = alt.layer(chart, title = title)
        return chart

    if plotId == 2:
        plot, rule = get_plot(table, 'OpponentScore', ["#4682b4", "darkblue"])
        chart = (plot + rule).properties(width=750)
        title = "Scoring along the " + season + " season by the opponents of " + team

        chart = alt.layer(chart, title = title)
        return chart

    if plotId == 3:
        plot1, rule1 = get_plot(table, 'TeamScore', ["#4682b4", "darkblue"])
        chart1 = (plot1 + rule1)

        plot2, rule2 = get_plot(table, 'OpponentScore', ["indianred", "darkred"])
        chart2 = (plot2 + rule2)

        chart = (chart1 + chart2).properties(width=750)
        title = "Scoring values along the " + season + " by " + team

        chart = alt.layer(chart, title = title)
        return chart

    if plotId == 4:
        chart, rule = get_plot(table, 'Difference', ["#4682b4", "darkblue"])
        chart = (chart + rule).properties(width=750)
        title = "Scoring difference along the " + season + " by " + team

        chart = alt.layer(chart, title = title)
        return chart
    raise ValueError(f"Value for {plotId} was incorrect. It must be between 1 and 4")