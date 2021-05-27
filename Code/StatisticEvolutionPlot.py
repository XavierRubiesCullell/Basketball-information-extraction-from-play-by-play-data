import altair as alt

def main(team, season, statistic, category, player, table):
    '''
    This function returns the plot of the evolution of a statistic during the season
    - statistic: statistic that we want to plot, in order to use it as an axis name (string)
    - category: category we want to study in case the statistic is "box score" (string)
    - player: player we want to study in case the statistic is "box score" (string)
    - table: values we want to plat (pandas.DataFrame)
    '''
    chart = alt.Chart(
        table.reset_index().dropna()
    ).mark_line(
        point=True
    ).encode(
        x = alt.X('index:T', title = "match"),
        y = alt.Y('Value:Q', title = "value"),
        tooltip = ['Date:T', 'Opponent:N', 'Value:Q']
    ).add_selection(
        alt.selection_single()
    )

    if statistic == "box score":
        statistic = category
        author = player
    else:
        author = team
        if statistic == "streak":
            statistic = "Greatest scoring streak"
        elif statistic == "partial":
            statistic = "Greatest partial"
        elif statistic == "drought":
            statistic = "Longest scoring drought"
        
    chart = alt.layer(chart, title = statistic + " along the " + season + " season by " + author)

    rule = alt.Chart(table).mark_rule(color='darkblue').encode(
        y = alt.Y('mean(Value):Q')
    )
    return (chart + rule).properties(width=750)