from clickhouse_driver import Client
from utils import bold

def set_percentage_column(df, groupby: str = 'timestamp', ):
    if (groupby in df):
        percent = df.groupby('timestamp')[percent_names[1]]


def legend_labels_percent_parse(df, percent_names, no_perc_labels):
    if ('timestamp' in df):
        percentages = df.groupby('timestamp')[percent_names[1]].apply(
            lambda x: (x / x.sum() * 100)
        )
    else:
        percentages = (df[percent_names[1]] / df[percent_names[1]].sum() * 100)

    percentages = percentages.round(3)
    df['percentage'] = percentages.reset_index(drop=True)
    df['legend_labels'] = df[percent_names[0]].apply(bold)

    if (not no_perc_labels):
        df['legend_labels'] = df.apply(
            lambda x: x['legend_labels'] +
            bold(' (' + str(x['percentage']) + '%)'), axis=1)


def df_clickhouse_create(
    client: Client, query, plot_name='',
    percent_names=None, no_perc_labels: bool = False
):
    print(f'Creating {plot_name}')

    df = client.query_dataframe(query)

    if (percent_names):
        legend_labels_percent_parse(df, percent_names, no_perc_labels)

    return (df)


def sort_by_column(column, df, index):
    sorted_df = df.sort_values(by=column, ascending=False)
    sorted_df = sorted_df.reset_index(drop=True)

    return (sorted_df[index].tolist())
