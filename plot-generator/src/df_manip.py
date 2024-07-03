from clickhouse_driver import Client
from utils import bold


def set_percentage_column(df, groupby: str = 'timestamp'):
    if (groupby in df):
        percent = df.groupby('timestamp')[percent_names[1]]


def legend_labels_percent_parse(df, percent_names, set_percent_labels: bool = True):
    '''
    `percent_names[0]` -> names\n
    `percent_names[1]` -> values
    '''
    percentages = (df[percent_names[1]] / df[percent_names[1]].sum() * 100)
    percentages = percentages.round(3)
    df['percentage'] = percentages.reset_index(drop=True)
    df['legend_labels'] = df[percent_names[0]].apply(bold)

    if (set_percent_labels):
        df['legend_labels'] = df.apply(
            lambda x: x['legend_labels'] +
            bold(' (' + str(x['percentage']) + '%)'), axis=1)


def df_clickhouse_create(
    client: Client, query, plot_name=''
):
    '''
    Print the plot being generated and get query dataframe.
    '''
    print(f'Creating {plot_name}')
    return (client.query_dataframe(query))


def sort_by_column(column, df, index):
    sorted_df = df.sort_values(by=column, ascending=False)
    sorted_df = sorted_df.reset_index(drop=True)

    return (sorted_df[index].tolist())
