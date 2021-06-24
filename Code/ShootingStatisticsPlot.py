# https://towardsdatascience.com/interactive-basketball-data-visualizations-with-plotly-8c6916aaa59e
import numpy as np
import plotly.graph_objects as go

# From: https://community.plot.ly/t/arc-shape-with-path/7205/5
def circumference_arc(xCenter=0.0, yCenter=0.0, r=10.5, startAngle=0.0, endAngle=2*np.pi):
    '''
    This function returns a circumference arc
    - xCenter: x coordinate of the center
    - yCenter: y coordinate of the center
    - r: circumference radius
    - startAngle: starting angle of the circumference
    - endAngle: ending angle of the circumference
    '''
    t = np.linspace(startAngle, endAngle, 200)
    x = xCenter + r * np.cos(t)
    y = yCenter + r * np.sin(t)
    path = f'M {x[0]}, {y[0]}'
    for k in range(1, len(t)):
        path += f'L{x[k]}, {y[k]}'
    return path

def draw_plotly_court(fig, shots, figWidth=600, margins=0):
    '''
    This function draws the basketball court and the shot lines
    - fig: figure object (plotly.graph_objs._figure.Figure)
    - shots: list of dictionaries, where each one represents a shot distance (list)
    - figWidth: defines the width of the figure (integer)
    - margins: defines the amount of padding around the sidelines (integer)
    '''
    figHeight = figWidth * (470 + 2 * margins) / (500 + 2 * margins)
    fig.update_layout(title="Shooting accuracy", title_x=0.425, font_size=10, width=figWidth, height=figHeight)
    fig.update_layout(width=figWidth+90)

    # Set axes ranges
    fig.update_xaxes(range=[-250 - margins, 250 + margins])
    fig.update_yaxes(range=[-52.5 - margins, 417.5 + margins])

    # mainLineCol = "#777777"
    mainLineCol = "white"
    lineWidth = 3

    fig.update_layout(
        # Line Horizontal
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
        plot_bgcolor="#ffb366", # background color
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=True,
        ),
        shapes=[
            # half court
            # dict(
            #     type="rect", x0=-250, y0=-52.5, x1=250, y1=417.5,
            #     line=dict(color=mainLineCol, width=lineWidth),
            #     # fillcolor='#333333',
            #     layer='below'
            # ),
            dict(
                type="line", x0=-250, y0=-52.5, x1=250, y1=-52.5,
                line=dict(color=mainLineCol, width=lineWidth),
            ),
            # zone
            dict(
                type="rect", x0=-80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color=mainLineCol, width=lineWidth),
                # fillcolor='#333333',
                layer='below'
            ),
            # inner zone
            dict(
                type="rect", x0=-60, y0=-52.5, x1=60, y1=137.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # free throw circle
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # hoop support
            dict(
                type="rect", x0=-2, y0=-7.25, x1=2, y1=-12.5,
                line=dict(color="#ec7607", width=1),
                fillcolor='#ec7607',
            ),
            # hoop
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=1),
            ),
            # board
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color="#ec7607", width=2),
            ),
            # semicircle
            dict(
                type="path",
                path=circumference_arc(r=40, startAngle=0, endAngle=np.pi),
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # three point semicircle
            dict(
                type="path",
                path=circumference_arc(r=237.5, startAngle=0.386283101, endAngle=np.pi - 0.386283101),
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # three point left line
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=89.47765084,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # three point right line
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=89.47765084,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # left timeout line
            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # right timeout line
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # lateral lines in the zone: 
            dict(
                type="line", x0=-90, y0=17.5, x1=-80, y1=17.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            dict(
                type="line", x0=-90, y0=27.5, x1=-80, y1=27.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            dict(
                type="line", x0=-90, y0=57.5, x1=-80, y1=57.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            dict(
                type="line", x0=-90, y0=87.5, x1=-80, y1=87.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            dict(
                type="line", x0=90, y0=17.5, x1=80, y1=17.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            dict(
                type="line", x0=90, y0=27.5, x1=80, y1=27.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            dict(
                type="line", x0=90, y0=57.5, x1=80, y1=57.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            dict(
                type="line", x0=90, y0=87.5, x1=80, y1=87.5,
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            ),
            # logo semicircle
            dict(
                type="path",
                path=circumference_arc(yCenter=417.5, r=60, startAngle=-0, endAngle=-np.pi),
                line=dict(color=mainLineCol, width=lineWidth),
                layer='below'
            )
        ] + shots
    )
    fig.update_layout(legend_title_text="Accuracy (%)")

    return fig


def color_election(acc):
    '''
    This function returns a color code given a shooting accuracy
    - acc: accuracy from a determined distance
    '''
    if acc < 20:
        return 0
    if acc < 40:
        return 1
    if acc < 60:
        return 2
    if acc < 80:
        return 3
    if acc < 95:
        return 4
    return 5


def treat_distance(row, total, shots, colors, accUsed):
    '''
    This function returns the line representing a shooting distance
    - row: row of the shot table, representing the values from a distance (pandas.Series)
    - total: total number of attempted shots (integer)
    - shots: shooting lines (list)
    - colors: color map vector (list)
    - accUsed: list of accuracy intervals, telling whether they are present on the map (list)
    '''
    colorId = color_election(row[4])

    # 22 ft == 220.5
    d = int(row[0])*220.5/22
    shots.append(dict(
        type="path",
        path=circumference_arc(r=d, startAngle=0, endAngle=np.pi),
        line=dict( color=colors[colorId], width=max(np.sqrt(row[3]/total*100), 0.2) ),
        layer='below'
    ))

    accUsed[colorId] = True


def legend_creation(accUsed, fig, colors, accuracies):
    '''
    This function creates the points that generate the legend elements
    - accUsed: boolean vector stating if the accuracy is on the map (list)
    - fig: ploty.graph_objects figure
    - colors: color map vector (list)
    - accuracies: legend labels (list)
    '''
    for i in range(len(accUsed)):
        if accUsed[i]:
            fig.add_trace(go.Scatter(
                x=[1000],
                y=[1000],
                marker=dict(
                    size=0,
                    color=colors[i],
                ),
                name=accuracies[i]
            ))


def main(shotTable):
    '''
    This function returns a plot given a table of records
    - shotTable: table with the shooting records
    '''
    colors = ('#B1E1AE', '#63C07D', '#1D9A6C', '#157F7A', '#1F6C55', '#23584B')
    accUsed = [False]*len(colors)
    accuracies = (
        "[0, 20)", "[20, 40)", "[40, 60)", "[60, 80)", "[80, 95)", "[95, 100)"
    )

    fig = go.Figure()
    total = shotTable.loc['TOTAL','Shots attempted']
    shotTable = shotTable.drop(index = ['TOTAL'], errors='ignore')
    shots = []
    for _, row in shotTable.iterrows():
        treat_distance(row, total, shots, colors, accUsed)

    legend_creation(accUsed, fig, colors, accuracies)

    return draw_plotly_court(fig, shots, figWidth=600, margins=0)