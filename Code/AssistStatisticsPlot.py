import pandas as pd
import altair as alt

def auxiliary_table(assistMatrix):
    '''
    This function returns a table in a format which is accepted by altair
    - assistMatrix: assist matrix, where M[i][j] indicates the number of assists from player i to player j (pandas.DataFrame)
    '''
    cols = ['Passer', 'Receiver', '# Assists']
    assistTable = pd.DataFrame(columns=cols)
    for i in range(len(assistMatrix.index)):
        for j in range(len(assistMatrix.columns)):
            if assistMatrix.index[i] != "TOTAL" and assistMatrix.columns[j] != "TOTAL":
                row = pd.Series([assistMatrix.index[i], assistMatrix.index[j], assistMatrix.iloc[i,j]], index=cols)
                assistTable = assistTable.append(row, ignore_index=True)
    return assistTable


def main(assistMatrix):
    '''
    This function returns a heatmap plot from an assist table
    - assistMatrix: assist matrix, where M[i][j] indicates the number of assists from player i to player j (pandas.DataFrame)
    '''
    assistTable = auxiliary_table(assistMatrix)

    chart = alt.Chart(assistTable).mark_rect().encode(
        x='Receiver:N',
        y='Passer:N',
        color='# Assists:Q'
    )
    return chart