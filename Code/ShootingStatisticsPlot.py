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
    fig_height = figWidth * (470 + 2 * margins) / (500 + 2 * margins)
    fig.update_layout(title="Shooting accuracy", font_size=10, width=figWidth, height=fig_height)

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
        plot_bgcolor="#ffd699",
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
            dict(
                type="rect", x0=-250, y0=-52.5, x1=250, y1=417.5,
                line=dict(color=mainLineCol, width=lineWidth),
                # fillcolor='#333333',
                layer='below'
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
    return fig


def color_election(acc):
    '''
    This function returns a colour code given a shooting accuracy
    - acc: accuracy from a determined distance
    '''
    if acc < 10:
        return '#DEEDCF'
    if acc < 20:
        return '#BFE1B0'
    if acc < 30:
        return '#99D492'
    if acc < 40:
        return '#74C67A'
    if acc < 50:
        return '#56B870'
    if acc < 60:
        return '#39A96B'
    if acc < 70:
        return '#1D9A6C'
    if acc < 80:
        return '#0C9462'
    if acc < 90:
        return '#008B57'
    if acc < 100:
        return '#007E4B'
    return '#006C3E'


def shot_line(row, total):
    '''
    This function returns the line representing a shooting distance
    - row: row of the shot table, representing the values from a distance (pandas.Series)
    - total: total number of attempted shots (integer)
    '''
    # 22 ft == 237.5
    # 25 ft == 240
    d = int(row.name)*240/25
    return dict(
        type="path",
        path=circumference_arc(r=d, startAngle=0, endAngle=np.pi),
        # line=dict(color="green", width=1), # same colour and width
        # line=dict(color="green", width=0.15*row[1]), # same colour
        # line=dict(color=color_election(row), width=1), # same width
        line=dict(color=color_election(row[2]), width=np.sqrt(row[1]/total*100)),
        layer='below'
    )


def main(shotTable):
    '''
    This function returns a plot given a table of records
    - shotTable: table with the shooting records
    '''
    fig = go.Figure()
    total = shotTable.loc['TOTAL','Shots attempted']
    shotTable = shotTable.drop(index = ['TOTAL'], errors='ignore')
    shots = []
    for _, row in shotTable.iterrows():
        shots.append(shot_line(row, total))

    return draw_plotly_court(fig, shots, figWidth=600, margins=0)